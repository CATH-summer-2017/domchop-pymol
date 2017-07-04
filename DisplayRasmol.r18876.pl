#!/usr/bin/env perl

#####
#  DisplayRasmol.pl
# 
#  Based on display_rasmol.php by Mark Dibley and Akpor Adrian Edo-Ukeh
# 
#  All purpose script for displaying rasmols
#
#  Parameters (*=Mandatory parameter)
#  * id                   - The thing to be displayed (Accession ID, PDB file, rasmol script or XML superposition file)
#    colouring            - The way to colour the structure(s) ('chain', 'chopping', 'struc' or 'comparedchopping')
#    comparedchoppingswap - When using comparedchopping colouring, swap the colours of the query and match
#    highlight            - The section to highlight (Chain ID, or a Domain ID)
#    noreplaceheader      - Do not replace the header of a rasmol script
#    cathversion          - The CATH version to display data from (one of CV_CURRENT, CV_LATEST_RELEASE, CV_V3_0_0,...)
#    matchordering        - The ordering of the matches in multiple superpositions (eg matchordering=NOMATCH:1gl2A00)
#
#  If the colouring is 'chopping' or 'comparedchopping', the script must know the chopping to use.
#  If no chopping is provided via parameters, the script will attempt to obtain one from the CathDB.
#  
#  To specify choppings, use one of the parameters:
#    chopping{id}    - The chopping in the format "10gs D2-78[A]+187-208[A] D79-186[A] F209-209[A]"
#    domall           - The chopping in the format "1.2.78.187.208:2.79.186"
#
# Notes on specifying choppings:
#  - You are **strongly urged** to use the chopping format for new work rather than the domall format.
#    The domall format is only included for backwards compatibilty with display_rasmol.php
#  - You are **strongly urged** to produce this the chopping format using the newCgiLine method of the Chopping class.
#    This ensures that your code will still work if/when this format is updated in the future.
#  - You may specify multiple choppings where appropriate by appending an accession id to the chopping parameter name.
#
#####

#####
# Use some standard Perl libraries
#####
use strict;
use perl5lib;
use English qw/ -no_match_vars /;
use Data::Dumper;
use XML::Simple;
use UNIVERSAL qw(isa);

#####
# Changing the XML parser that XML::Simple uses to XML::Parser appears to help
# with problems of calls to XML::Simple taking up more memory on each call
#####
$XML::Simple::PREFERRED_PARSER = 'XML::Parser';

my $BIOPTOOLS_DIR = '/opt/local/apps/linux/bioptools/';

#####
# Use some CATH libraries
#####
use CathCGI;
use CathCGI::Update;
use CathDB;
use Exception;
use CathData;
use ReadCathParam;
use ReadColourList;

#####
# Provide prototypes for the subroutines in this script
#####
sub ProcessSsapXml($);
sub getChoppings ($$);

#####
# Declare some constants to be used in this script
#####
use constant COLOURING_BY_CHAIN => "COLOURING_BY_CHAIN";
use constant COLOURING_BY_CHOPPING => "COLOURING_BY_CHOPPING";
use constant COLOURING_BY_COMPAREDCHOPPING => "COLOURING_BY_COMPAREDCHOPPING";
use constant COLOURING_BY_STRUC => "COLOURING_BY_STRUC";

#####
# Set the path to a simple and safe path for security
# (otherwise the taint option produces errors)
#####
$ENV{'PATH'} = "/sbin:/bin:/usr/bin:/usr/local/svn/trunk/bin/";

#####
# The filesystems that files can be read from
# In the future, it would be nice to incorporate these into the CathParam file
# and write a standard module for parsing them
#####
my @acceptableDeviceNames = (
	"/cath/data",
	"/cath/data/current",
	"/cath/data/v3_0_0",
	"/cath/data/v3_1_0",
	"/cath/data/v3_2_0",
	"/cath/data/v3_3_0",
	"/cath/data/v3_4_0",
	"/cath/data/v3_5_0",
	"/cath/data/v4_0_0",
	"/cath/data/v4_1_0",
	"/cath/people",
	"/cath/cathwww",
	"/cath/httpd",
	"/cath/godzilla-data1",
	"/cath/kingkong-data1",
);

#####
# Construct a new CGI object
#####
my $cgi = new CGI();
if (!defined($cgi)) {
	CathCGI::abort(new Exception("Unable to initialise a CGI object"));
}

#####
# Attempt to construct a CathCGI 
#####
my $cathCgi = new CathCGI::Update();
if (!defined($cathCgi) || !$cathCgi) {
	CathCGI::abort(new Exception("Unable to initialise a CathCGI object"));
}

#####
# Grab the CATH parameters
#####
my $gParam = ReadCathParam();
if (!defined($gParam) || ref($gParam) ne "HASH" || scalar(keys(%$gParam)) <= 0) {
	CathCGI::abort(new Exception("Unable to read the CATH parameter file"));
}

#####
# Grab the CATH_UPDATE_SSAP_XML_SUP_DIR parameter
#####
my $xmlSupDir = $gParam->{'CATH_UPDATE_SSAP_XML_SUP_DIR'};
if (!defined($xmlSupDir)) {
	CathCGI::abort(new Exception("Unable to read the CATH_UPDATE_SSAP_XML_SUP_DIR parameter"));
}

#####
# Grab the required parameters from CathCGI
#
# 1. The 'id' parameter
#####
my @displayIds = CathCGI::param('id');
my $displayId = CathCGI::param('id');
if (!defined($displayId)) {
	$displayId = CathCGI::param('query_id');
}
if (!defined($displayId)) {
	$displayId = CathCGI::param('location');
}
if (!defined($displayId)) {
	my $displayId1 = CathCGI::param('id1');
	my $displayId2 = CathCGI::param('id2');
	if (!CathData::isValidAccessionCode($displayId1) || !CathData::isValidAccessionCode($displayId2)) {
		CathCGI::abort new Exception("No valid id parameter passed.\nPlease pass an id parameter or id1 and id2 parameters.");
	}
	my $displayId1Prefix = substr($displayId1,0,2);
	$displayId = "$xmlSupDir/$displayId1Prefix/$displayId1/$displayId1$displayId2.superpose.xml";
}

#####
# 2. The 'colouring' parameter
#####
my $colouringType = undef;
my $colouring = CathCGI::param('colouring');
if (defined($colouring) && ref($colouring) eq "") {
	$colouring = uc($colouring);
	if ($colouring eq "CHAIN") {
		$colouringType = COLOURING_BY_CHAIN;
	}
	if ($colouring eq "CHOPPING") {
		$colouringType = COLOURING_BY_CHOPPING;
	}
	if ($colouring eq "COMPAREDCHOPPING") {
		$colouringType = COLOURING_BY_COMPAREDCHOPPING;
	}
	if ($colouring eq "STRUC") {
		$colouringType = COLOURING_BY_STRUC;
	}
}

#####
# 3. The 'comparedchoppingswap' parameter
#####
my $comparedChoppingSwap = CathCGI::param('comparedchoppingswap');
if ($comparedChoppingSwap && $colouringType ne COLOURING_BY_COMPAREDCHOPPING) {
	CathCGI::abort(new Exception("'comparedchoppingswap' parameter may only be used with 'comparedchopping' colouring"));
}

#####
# 4. The 'highlight' parameter
#####
my $highlight = CathCGI::param('highlight');
if (defined($highlight) && !CathData::isValidAccessionCode($highlight)) {
	CathCGI::abort(new Exception("Highlight parameter \"$highlight\" is not a valid CATH accession ID"));
}

#####
# 5. The 'noreplaceheader' parameter
#####
my $noReplaceHeader = CathCGI::param('noreplaceheader') || '';
if ($noReplaceHeader =~ /^[nNfF]/) {
	$noReplaceHeader = 0;
}

#####
# 6. The 'cathversion' parameter
#####
my $cathVersion = CathCGI::param('cathversion');
my $cathVersionMethodText = "";
my $cathVersionText = "";
my $cathdb;

#####
# 7. The 'matchordering' parameter
#####
my $matchOrdering = CathCGI::param('matchordering') || '';
my %orderingOffsetOfMatch;
my @matchOrderingEntries = split(/\:/, $matchOrdering);
for (my $matchOrderingCtr = 0; $matchOrderingCtr < scalar(@matchOrderingEntries); $matchOrderingCtr++) {
	my $matchOrderingEntry = $matchOrderingEntries[$matchOrderingCtr];
	if ($matchOrderingEntry ne "NOMATCH") {
		$orderingOffsetOfMatch{$matchOrderingEntry} = $matchOrderingCtr;
	}
}

#####
# If there is a CATH version, then check it is valid and then connect to the correct database
#####
if ($cathVersion) {
	#####
	# Call CathData::filenameOfAccessionCode() to check that the CATH version is valid
	#####
	if (!CathData::isValidCathVersion($cathVersion)) {
		CathCGI::abort(new Exception("Unable to retrieve filenames with CATH version \"$cathVersion\"", CathData::getException()), 0);
	}
	$cathVersionMethodText = "(set using the CGI param cathversion=$cathVersion)";
	
	#####
	# Construct a CathDB object using the CATH version
	#####
	$cathdb = new CathDB($cathVersion);
	if (!isa($cathdb, "CathDB")) {
		CathCGI::abort(new Exception("Unable to construct a CATH database from the CATH version \"$cathVersion\"", CathDB::getException()));
	}
}
#####
# Else if no CATH version has been set, get a CATH database from the session
#####
else {
	$cathdb = $cathCgi->getCathDB;
	if (!isa($cathdb, "CathDB")) {
		CathCGI::abort(new Exception("Unable to obtain a connection to the CATH database", CathDB::getException()));
	}
	$cathVersionMethodText = "(determined from the session)";
}

#####
# Determine the version from the database
# and if $cathVersion is not already set, set it to use the correct data
#####
my $databaseVersion = $cathdb->{'db'};
$databaseVersion =~ s/^cathdb_//g;
$databaseVersion =~ s/^cathdb//g;
if (!$cathVersion) {
	if ($databaseVersion eq "current" || $databaseVersion eq "test1" || $databaseVersion eq "cathdbtest2") {
		$cathVersion = "CV_CURRENT";
	}
	elsif ($databaseVersion eq "v3_0_0") {
		$cathVersion = "CV_V3_0_0";
	}
	elsif ($databaseVersion eq "v3_1_0") {
		$cathVersion = "CV_V3_1_0";
	}
	elsif ($databaseVersion eq "v3_2_0") {
		$cathVersion = "CV_V3_2_0";
	}
	elsif ($databaseVersion eq "v3_3_0") {
		$cathVersion = "CV_V3_3_0";
	}
	elsif ($databaseVersion eq "v3_4_0") {
		$cathVersion = "CV_V3_4_0";
	}
	elsif ($databaseVersion eq "v3_5_0") {
		$cathVersion = "CV_V3_5_0";
	}
	elsif ($databaseVersion eq "v4_0_0") {
		$cathVersion = "CV_V4_0_0";
	}
	elsif ($databaseVersion eq "v4_1_0") {
		$cathVersion = "CV_V4_1_0";
	}
}

#####
# Check for invalid inputs
#####
if (!defined($displayId)) {
	CathCGI::abort(new Exception("No ID (file or accession code) specified"));
}

#####
# Read the standard CATH colour list program
#####
my $colourList = ReadColourList();
if (!defined($colourList) || !$colourList || ref($colourList) ne "ARRAY") {
	CathCGI::abort(new Exception("Unable to parse standard CATH colour list", ReadColourList::getException()));
}

#####
# Attempt to read the cath parameters file
#####
my $param = ReadCathParam();
if (!defined($param) || !$param || ref($param) ne "HASH") {
	CathCGI::abort(new Exception("Unable to parse CATH parameters file"));
}

#####
# If an accession ID has been specified, then determine which file to display
#####
my %chainCodeOfAccessionId;
my $displayFilename = $displayId;
if (CathData::isValidAccessionCode($displayFilename,1)) {
	$displayFilename = CathData::filenameOfAccessionCode($displayId, CathData::FILETYPE_PDB, $cathVersion);
	if (!$displayFilename) {
		CathCGI::abort(new Exception("Unable to form filename for \"$cathVersion\" with CATH version \"$cathVersion\""));
	}
	$chainCodeOfAccessionId{$displayId} = 1;
	$cathVersionText = "echo CATH version : $databaseVersion $cathVersionMethodText";
}

#####
# Ensure that the file is held on a valid file system
#####
my %acceptableDeviceIds;
foreach my $deviceName (sort(@acceptableDeviceNames)) {
	$acceptableDeviceIds{(stat($deviceName))[0]} = 1;
} 
if (!defined((stat($displayFilename))[0]) || !-s $displayFilename) {
	CathCGI::abort(new Exception("Cannot access \"$displayFilename\". This could be because no such non-empty file exists or because it is not accessible."));
}

if ( !defined($acceptableDeviceIds{(stat($displayFilename))[0]}) ) {
    CathCGI::abort(new Exception("Cannot access \"$displayFilename\". This file is located on a device that has not been authorised."));
}

#####
# Attempt to read the file into a string
#####
my $displayFH;
if (!open $displayFH, "<$displayFilename") {
	CathCGI::abort(new Exception("Unable to open \"$displayFilename\" for reading : $OS_ERROR"));
}
my @fileLines = (<$displayFH>);
my $fileString = join("\n", @fileLines);
close $displayFH;

#####
# Determine what sort of file it is and process accordingly
#####
my %chainCodes;
my $colourLines;
my $pdbData = "";
my $rasmolHeader = "";

#####
# Check if the file is an xml file
# If so, process it as a SSAP XML output.
#####
if ($fileString =~ /^\s*<\?xml/) {
	my $ProcessSsapXml = ProcessSsapXml(\@displayIds);
	if (!defined($ProcessSsapXml) || !$ProcessSsapXml || ref($ProcessSsapXml) ne "ARRAY" || scalar(@$ProcessSsapXml) != 2) {
		CathCGI::abort(new Exception("ProcessSsapXml() did not return a valid value"));
	}
	my ($chainCodesHashRef, $accessionIdArray);
	($chainCodesHashRef, $pdbData) = @$ProcessSsapXml;
	foreach my $chainCode (sort(keys(%$chainCodesHashRef))) {
		$chainCodeOfAccessionId{$chainCodesHashRef->{$chainCode}} = $chainCode;
	}
	%chainCodes = %$chainCodesHashRef;
}
#####
# If the file is a PDB file
#####
elsif ($fileString =~ /^HEADER\s+/ || $fileString =~ /^ATOM\s+/ || $fileString =~ /^REMARK\s+/) {
	my $chainCodeOfAccessionIdRequired = (scalar(keys(%chainCodeOfAccessionId)) <= 0);
	my $pdbCode = "NDEF";
	foreach my $line (@fileLines) {
		#####
		# If this is the header line, parse the line for the accession ID
		#####
		if ($line =~ /^HEADER\s+(.*?)\s*(\d{2}\-\w{3}\-\d{2})\s+(\d\w{3})/) {
			$pdbCode = 1;
		}
		#####
		# Else, if this is an atom line, parse the line for a chain code
		#####
		elsif ($line =~ /^ATOM\s+/) {
			$pdbData .= "$line";
			my $chainCode = substr($line,21,1);
			$chainCodes{$chainCode} = 0;
			if ($chainCodeOfAccessionIdRequired) {
				$chainCodeOfAccessionId{$pdbCode.$chainCode} = $chainCode;
			}
		}
	}
}
#####
# If the file is a superposition file
#####
elsif ($fileString =~ /^#!rasmol/) {
	my $foundExit = 0;
	foreach my $line (@fileLines) {
			if (!$foundExit) {
				$rasmolHeader .= "$line";
				if ($line =~ /exit/) {
					$foundExit = 1;
				}
			}
			else {
				$pdbData .= "$line";
				my $chainCode = substr($line,21,1);
				if (defined($chainCode) && length($chainCode) == 1) {
					$chainCodes{$chainCode} = 0;
					$chainCodeOfAccessionId{"NDEF".$chainCode} = $chainCode;
				}
			}
	}
}
else {
	CathCGI::abort(new Exception("Unable to process file \"$displayFilename\""));
}

#####
# By now we should know the number of chains
# So use this to set the colouring parameter if it has not been set
#####
my $noOfChainCodes = scalar(keys(%chainCodes));
if ($noOfChainCodes <= 0) {
	CathCGI::abort(new Exception("Not found any chain codes"));
}
if (!defined($colouringType)) {
	if ($noOfChainCodes >= 1) {
		$colouringType = COLOURING_BY_CHAIN;
	}
	else {
		$colouringType = COLOURING_BY_STRUC;
	}
}

#####
# Grab any Choppings that have been passed as arguments
#####
my $choppings = getChoppings($cgi, \%chainCodeOfAccessionId);
if (!$choppings || ref($choppings) ne "HASH") {
	CathCGI::abort(new Exception("Unable to getChoppings", $choppings));
}

#####
# Find the smallest bit that we need a chopping for
#####
my %smallestChoppingsRequiredOfAccessionId;
if ($colouringType eq COLOURING_BY_CHOPPING || $colouringType eq COLOURING_BY_COMPAREDCHOPPING) {
	%smallestChoppingsRequiredOfAccessionId = map {($_ => $_)} keys(%chainCodeOfAccessionId);
}
elsif (Domain::isValidDomainId($highlight)) {
	$smallestChoppingsRequiredOfAccessionId{$highlight} = $highlight;
	if (defined($smallestChoppingsRequiredOfAccessionId{substr($highlight, 0, 5)})) {
		$smallestChoppingsRequiredOfAccessionId{substr($highlight, 0, 5)} = $highlight;
	}
}

#####
# Grab a Chopping for each of the bits that we need a Chopping for
#####
my %choppingOfAccessionId;
my $requireDatabaseChoppings = 0;
foreach my $accessionId (sort(keys(%smallestChoppingsRequiredOfAccessionId))) {
	my $accessionId = $smallestChoppingsRequiredOfAccessionId{$accessionId};
	my $chopping = $choppings->{$accessionId};
	if (!defined($chopping)) {
		if (length($accessionId) > 5) {
			$chopping = $choppings->{substr($accessionId, 0, 5)};
		}
	}
	if (!defined($chopping)) {
		if (length($accessionId) > 4) {
			$chopping = $choppings->{substr($accessionId, 0, 4)};
		}
	}
	if (!defined($chopping)) {
		$requireDatabaseChoppings = 1;
	}
	$choppingOfAccessionId{$accessionId} = $chopping;
}
#CathCGI::abort(new Exception(Dumper(\%chainCodeOfAccessionId)."\n".Dumper(\%smallestChoppingsRequiredOfAccessionId)."\n".Dumper(\%choppingOfAccessionId)));

#####
# Grab a chopping from the database if it will be needed
#####
if ($requireDatabaseChoppings) {	
	$cathVersionText = "echo CATH version : $databaseVersion $cathVersionMethodText";
	foreach my $accessionId (sort(keys(%choppingOfAccessionId))) {
		my $chopping = $choppingOfAccessionId{$accessionId};
		if (!defined($chopping)) {
			my $choppings = $cathdb->getChopping($accessionId, "PDB");
			if (!$choppings || ref($choppings) ne "ARRAY" || scalar(@$choppings) <= 0) {
				CathCGI::abort(new Exception("Unable to select any choppings from CATH database for structure \"$accessionId\"\n".Dumper($choppings), $cathdb->getException()));
			}
			if (scalar(@$choppings) > 1) {
				CathCGI::abort(new Exception("Found multiple choppings in CATH database for structure \"$accessionId\" : \n".Dumper($choppings)));
			}
			$choppingOfAccessionId{$accessionId} = $choppings->[0];
		}
	}
}


#####
# START Rasmol/PyMOL
#####

#####
# If we are to colour by chopping, then set the colour lines accordingly
#####
if ($colouringType eq COLOURING_BY_CHOPPING || Domain::isValidDomainId($highlight)) {
	foreach my $accessionId (sort(keys(%choppingOfAccessionId))) {
		my $chopping = $choppingOfAccessionId{$accessionId};
		my $choppingRasmolString = $chopping->toString({'STYLE' => 'RASMOL', 'HIGHLIGHT' => $highlight});
		if (!$choppingRasmolString) {
			CathCGI::abort new Exception("Unable to retrieve rasmol string from Chopping", $chopping->getException());
		}
		$colourLines .= $choppingRasmolString;
	}
}

#####
# If we are to colour by chain, then set the colour lines accordingly
#####
elsif ($colouringType eq COLOURING_BY_CHAIN) {
	
	my $chainCodes;
	@$chainCodes = sort(keys(%chainCodes));
	if (!defined($chainCodes) || !$chainCodes || ref($chainCodes) ne "ARRAY" || scalar(@$chainCodes) <= 0) {
		CathCGI::abort(new Exception("Unable to colour by chain as no valid chain codes array exists"));
	}
	$colourLines .= "echo\n";
	$colourLines .= "select *\n";
	my $echoString = ("echo\n"x40)."echo **************************\n";
	if (defined($chainCodes{' '})) {
		if (scalar(@$chainCodes) > 1) {
			$colourLines .= "colour white\n";
			$colourLines .= "echo Chain ' ' : White\n";
		}
		else {
			$colourLines .= "colour $colourList->[0]->{'name'}\n";
			my $chainName = "Chain ' '";
			if ($chainCodes{' '}) {
				$chainName = $chainCodes{' '};
			}
			$colourLines .= "echo $chainName : $colourList->[0]->{'name'}\n";
		}
		
		delete($chainCodes{' '});
		@$chainCodes = sort(keys(%chainCodes));
	}
	@$chainCodes = sort(@$chainCodes);
	
	for (my $chainCodeCtr = 0; $chainCodeCtr < scalar(@$chainCodes); $chainCodeCtr++) {
		my $chainCode = $chainCodes->[$chainCodeCtr];
		if (!defined($chainCode) || ref($chainCode) ne "" || length($chainCode) != 1) {
			CathCGI::abort(new Exception("Unable to colour by chain as one of the chain codes \"$chainCode\" is invalid"));
		}
		$colourLines .= "select *:$chainCode\n";
		if (Chain::isValidChainId($highlight) && substr($highlight, -1) ne $chainCode) {
			$colourLines .= "colour white\n";
			$colourLines .= "trace 40\n";
		}
		else {
			$colourLines .= "colour $colourList->[$chainCodeCtr]->{'name'}\n";
		}
		my $chainName = "Chain '$chainCode'";
		if ($chainCodes{$chainCode}) {
			$chainName = $chainCodes{$chainCode};
		}
		$echoString .= "echo $chainName : $colourList->[$chainCodeCtr]->{'name'}\n";
	}
	$echoString .= "echo **************************\n";
	$colourLines .= $echoString;
}

#CathCGI::abort(new Exception(Dumper(\%choppingOfAccessionId)));

#####
# If we are to colour by compared chopping, then set the colour lines accordingly
#####
elsif ($colouringType eq COLOURING_BY_COMPAREDCHOPPING) {
	#my %chainCodeOfAccessionId = map {($chainCodes{$_}, $_)} sort(keys(%chainCodes));
	my %lighteningOfChainCode = map {$_, 0.5} ('B'..'Z');
	$lighteningOfChainCode{'A'} = -0.075;
	if ($comparedChoppingSwap) {
		%lighteningOfChainCode = map {$_, -0.075} ('B'..'Z');
		$lighteningOfChainCode{'A'} = 0.5;
	}
	foreach my $chainCode (sort(keys(%chainCodes))) {
		my $accessionId = $chainCodes{$chainCode};
		my $chopping = $choppingOfAccessionId{$accessionId};
		my $orderingOffset = $orderingOffsetOfMatch{$accessionId};
		if (!defined($orderingOffset)) {
			$orderingOffset = 0;
			if ($chainCode ne 'A' && scalar(keys(%chainCodes)) > 2) {
				CathCGI::abort(new Exception("Unable to find matchordering entry for \"$accessionId\" but there are multiple superpositions"));
			}
		}
		$colourLines .= "select *$chainCode\n";
		$colourLines .= "select *$chainCode\n";
		my $lightening = $lighteningOfChainCode{$chainCode};
		$colourLines .= $chopping->toString({'COLOUROFFSET' => $orderingOffset, 'STYLE' => 'RASMOL', 'LIGHTEN' => $lightening, 'CHAINCODE' => $chainCode});
		#$colourLines .= $chopping->toString({'STYLE' => 'RASMOL', 'LIGHTEN' => $lightening});
		$colourLines .= "select *$chainCode\n";
		$colourLines .= "trace\n";
		$colourLines .= "select all\n";
	}
}

#####
# If we are to colour by secondary structure, then set the colour lines accordingly
#####
elsif ($colouringType eq COLOURING_BY_STRUC) {
	$colourLines .= "select *\n";
	$colourLines .= "trace\n";
	$colourLines .= "select sheet\n";
	$colourLines .= "colour yellow\n";
	$colourLines .= "cartoon\n";
	$colourLines .= "select helix\n";
	$colourLines .= "colour magenta\n";
	$colourLines .= "cartoon\n";
	$colourLines .= "select all\n";
}

if (!defined($rasmolHeader) || !$rasmolHeader || !$noReplaceHeader) {
	$rasmolHeader = <<_EOF;
#!rasmol -script

zap
load inline

select all
cartoon
set specular on
set specpower 40
set ambient 23
wireframe off
slab off
set bonds off
set axes off
set boundingbox off
set unitcell off
set bondmode and
dots off
select all
colour bonds none
colour backbone none
colour hbonds none
colour ssbonds none
colour ribbons none
trace
select helix,sheet
cartoon
select all
echo
$colourLines
$cathVersionText
select *
exit
_EOF
}

use Digest::MD5 qw/ md5_hex /;

my $filename = "rasmol-" . md5_hex($displayId) . "-$$.rasscript";

print "Content-Disposition: " . qq[attachment; filename="$filename"] . "\n";
print "Content-type: application/x-rasmol\n\n";
print "$rasmolHeader\n";
print "$pdbData\n";

#CathCGI::abort(new Exception("Finished"));

sub ProcessSsapXml($) {
	my ($ids) = @ARG;
	
	#####
	# Sanity check the parameters
	#####
	if (!defined($ids) || ref($ids) ne "ARRAY" || scalar(@$ids) <= 0) {
		CathCGI::abort(new Exception("No valid array of ids parameter passed"));
	}
	
	#####
	# Process each of the IDs
	#####
	my $baseId = undef;
	my $basePDB = undef;
	my $baseChainCode = "A";
	my @otherChainCodes = ("B".."Z");
	my @rotatedStructures;
	my $idCtr = 0;
	my %entityIdOfChainCode;
	foreach my $id (@$ids) {
		$idCtr++;
		if (!defined($id) || ref($id) ne "" || length($id) <= 0) {
			CathCGI::abort(new Exception("One of the ids is invalid"));
		}
		if (!-s $id) {
			CathCGI::abort(new Exception("No such XML file \"$id\""));
		}
		
		#####
		# Read in the file
		#####
		my $idFH;
		if (!open $idFH, "<$id") {
			CathCGI::abort(new Exception("Unable to open file \"$id\" for reading : $OS_ERROR"));
		}
		my @fileLines = (<$idFH>);
		my $xmlString = join("\n", @fileLines);
		close $idFH;
		
		#####
		# Attempt to parse the XML string
		#####
		my $oXmlSimple = new XML::Simple();
		my $ref = $oXmlSimple->XMLin($xmlString);
		if (!defined($ref) || ref($ref) ne "HASH") {
			CathCGI::abort(new Exception("Unable to parse file \"$displayFilename\""));
		}
		
		#####
		# Grab and check the ids from the XML data structure...
		#####
		my ($id1, $id2) = ($ref->{'structure1'}->{'id'}, $ref->{'structure2'}->{'id'});
		my ($file1, $file2) = ($id1, $id2);
		foreach my $file ($file1, $file2) {
			if (!defined($file) || !CathData::isValidAccessionCode($file)) {
				CathCGI::abort (new Exception("Unable to parse a valid structure ID from superposition file \"$displayFilename\""));
			}
			elsif (length($file) == 6) {
				$file = substr($file, 0, 5)."0".substr($file, 5, 1);
			}
			$cathVersionText = "echo CATH version : $databaseVersion $cathVersionMethodText";
			$file = CathData::filenameOfAccessionCode($file, CathData::FILETYPE_PDB, $cathVersion);
			if (!$file) {
				CathCGI::abort(new Exception("Unable to retrieve filenames with CATH version \"$cathVersion\"", CathData::getException()));
			}
			if (!-s $file) {
				CathCGI::abort (new Exception("No such non-empty PDB file \"$file\" exists\n"));
			}
		}
		
		#####
		# Record the base ID or check that it is consistent if it has been set previously
		#####
		if (!defined($baseId)) {
			$baseId = $id1;
		}
		else {
			if ($baseId ne $id1) {
				CathCGI::abort(new Exception("The previous base (query) id is \"$baseId\" - cannot also superpose against a base of \"$id1\""));
			}
		}
		
		#####
		# Grab and check the centres from the XML data structure...
		#####
		my ($centre1, $centre2) = ($ref->{'structure1'}->{'centre'}, $ref->{'structure2'}->{'centre'});
		foreach my $centre ($centre1, $centre2) {
			if (!defined($centre) || !$centre || ref($centre) ne "HASH") {
				CathCGI::abort (new Exception("Unable to parse a valid centre from superposition file \"$displayFilename\" ".Dumper($centre)));
			}
		}
		
		#####
		# 
		#####
		my ($centre1X, $centre1Y, $centre1Z) = ($centre1->{'x'}, $centre1->{'y'}, $centre1->{'z'});
		my ($centre2X, $centre2Y, $centre2Z) = ($centre2->{'x'}, $centre2->{'y'}, $centre2->{'z'});
		foreach my $centreCoord ($centre1X, $centre1Y, $centre1Z, $centre2X, $centre2Y, $centre2Z) {
			if (!defined($centreCoord) || ref($centreCoord) ne "" || $centreCoord !~ /^[\d\-\.]+$/) {
				CathCGI::abort (new Exception("Unable to parse a valid centre's coordinates from superposition file \"$displayFilename\""));
			}
			$centreCoord = -$centreCoord;
		}
		
		#####
		# Grab and check the rotation from the XML data structure...
		#####
		my $rotation = $ref->{'rotationmatrix'};
		if (!defined($rotation) || !$rotation || ref($rotation) ne "HASH") {
			CathCGI::abort (new Exception("Unable to parse a valid rotationmatrix from superposition file \"$displayFilename\""));
		}
		my @rotStrings;
		my ($row1, $row2, $row3) = ($rotation->{'row1'}, $rotation->{'row2'}, $rotation->{'row3'});
		foreach my $row ($row1, $row2, $row3) {
			if (!defined($row) || !$row || ref($row) ne "HASH") {
				CathCGI::abort (new Exception("Unable to parse a valid rotationmatrix row from superposition file \"$displayFilename\""));
			}
			my ($col1, $col2, $col3) = ($row->{'col1'}, $row->{'col2'}, $row->{'col3'});
			foreach my $col ($col1, $col2, $col3) {
				if (!defined($col1) || ref($col1) ne "" || $col1 !~ /^[\d\-\.]+$/) {
					CathCGI::abort (new Exception("Unable to parse a valid rotationmatrix col from superposition file \"$displayFilename\""));
				}
				push @rotStrings, $col;
			}
		}
		
		#####
		# Parse through the resulting data
		# Change the chain codes to A and B respectively
		# Remove any TER records
		#####
		if (!defined($basePDB)) {
			my $catCommand = "cat \"$file1\"";
			$basePDB = `$catCommand`;
			my @basePDBLines = split(/\n/, $basePDB);
			$basePDB = "";
			$entityIdOfChainCode{$baseChainCode} = $id1;
			foreach my $basePDBLine (@basePDBLines) {
				if ($basePDBLine =~ /^ATOM/) {
					$basePDBLine = substr($basePDBLine,0,21).$baseChainCode.substr($basePDBLine,22);
				}
				if ($basePDBLine !~ /^TER/) {
					$basePDB .= "$basePDBLine\n";
				}
			}
		}
		
		#####
		# Translate and rotate the structures as necessary
		#####
		my $rotString = join(" ", @rotStrings);
		my $rotateCommand = "$BIOPTOOLS_DIR/pdbtranslate -x $centre2X -y $centre2Y -z $centre2Z \"$file2\" | $BIOPTOOLS_DIR/pdbrotate -n -m $rotString | $BIOPTOOLS_DIR/pdbtranslate -x ".(-$centre1X)." -y ".(-$centre1Y)." -z ".(-$centre1Z);
		my $rotatedStructure = `$rotateCommand`;
		
		#####
		# Determine the correct chain code for this structure
		#####
		if ($idCtr > scalar(@otherChainCodes)) {
			CathCGI::abort(new Exception("Unable to superpose more than ".scalar(@otherChainCodes)." structures"));
		}
		my $rotateStructureChainCode = $otherChainCodes[$idCtr-1];
		if (!defined($rotateStructureChainCode) || ref($rotateStructureChainCode) || $rotateStructureChainCode !~ /^\w$/) {
			CathCGI::abort(new Exception("Invalid chain code to use in superposition : \"$rotateStructureChainCode\""));
		}
		$entityIdOfChainCode{$rotateStructureChainCode} = $id2;
		
		#####
		# Parse through the resulting data
		# Change the chain code to $rotateStructureChainCode
		# Remove any TER records
		#####
		my @rotatedStructureLines = split(/\n/, $rotatedStructure);
		$rotatedStructure = "";
		foreach my $rotatedStructureLine (@rotatedStructureLines) {
			if ($rotatedStructureLine =~ /^ATOM/) {
				$rotatedStructureLine = substr($rotatedStructureLine,0,21).$rotateStructureChainCode.substr($rotatedStructureLine,22);
			}
			if ($rotatedStructureLine !~ /^TER/) {
				$rotatedStructure .= "$rotatedStructureLine\n";
			}
		}
		
		push @rotatedStructures, $rotatedStructure;
	}
	
	#CathCGI::abort(new Exception(Dumper([\%entityIdOfChainCode, $basePDB.join("", @rotatedStructures)])));
	return [\%entityIdOfChainCode, $basePDB.join("", @rotatedStructures)];
}

sub getChoppings ($$) {
	my ($cgi, $accessionIds) = @ARG;
	
	#####
	# Sanity check the parameters
	#####
	if (!defined($cgi) || !isa($cgi, "CGI")) {
		return new Exception("No valid accession IDs argument");
	}
	if (!defined($accessionIds) || ref($accessionIds) ne "HASH" || scalar(keys(%$accessionIds)) <= 0) {
		return new Exception("No valid accession IDs argument");
	}
	
	my %choppingOfId;
	
	my @cgiParams = $cgi->param();
	foreach my $cgiParam (sort(@cgiParams)) {
		if ($cgiParam =~ /^domall(.*)$/i) {
			my $id = $1;
			my $cgiValue = $cgi->param($cgiParam);
			my $chopping = new Chopping();
			my $parseOldCgiLineResult = $chopping->parseOldCgiLine($cgiValue);
			if (!$parseOldCgiLineResult) {
				CathCGI::abort(new Exception("Unable to parse a Chopping from \"$cgiValue\""));
			}
			$choppingOfId{$id} = $chopping;
		}
		elsif ($cgiParam =~ /^chopping(.*)$/i) {
			my $id = $1;
			my $cgiValue = $cgi->param($cgiParam);
			my $chopping = new Chopping();
			my $parseNewCgiLineResult = $chopping->parseNewCgiLine($cgiValue);
			if (!$parseNewCgiLineResult) {
				CathCGI::abort(new Exception("Unable to parse a Chopping from \"$cgiValue\"", $chopping->getException()));
			}
			$choppingOfId{$id} = $chopping;
		}
	}
	
	#die Dumper(\%choppingOfId);
	
	return \%choppingOfId;
}

