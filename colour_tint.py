'''
newR = currentR + (255 - currentR) * tint_factor
newG = currentG + (255 - currentG) * tint_factor
newB = currentB + (255 - currentB) * tint_factor
'''
import pprint

dom1 = "dom1"
dom2 = "dom2"
dom3 = "dom3"
dom4 = "dom4"
dom5 = "dom5"
dom6 = "dom6"
dom7 = "dom7"
dom8 = "dom8"
dom9 = "dom9"
dom10 = "dom10"
dom11 = "dom11"
dom12 = "dom12"
dom13 = "dom13"
dom14 = "dom14"
dom15 = "dom15"
dom16 = "dom16"
dom17 = "dom17"
dom18 = "dom18"
dom19 = "dom19"
dom20 = "dom20"
dom21 = "dom21"
dom22 = "dom22"
dom23 = "dom23"



dict_of_colours = { #original colours
     dom1  :  [0, 0, 255],
     dom2  :  [255, 0, 0],
     dom3  :  [0, 255, 0],
     dom4  :  [255, 255, 0],
     dom5  :  [255, 100, 117],
     dom6  :  [127, 127, 127],
     dom7  :  [159, 31, 239],
     dom8  :  [174, 213, 255],
     dom9  :  [139, 239, 139],
     dom10  :  [255, 164, 0],
     dom11  :  [0, 255, 255],
     dom12  :  [174, 117, 88],
     dom13  :  [45, 138, 86],
     dom14  :  [255, 0, 100],
     dom15  :  [255, 0, 255],
     dom16  :  [255, 171, 186],
     dom17  :  [246, 246, 117],
     dom18  :  [255, 156, 0],
     dom19  :  [152, 255, 179],
     dom20  :  [255, 69, 0],
     dom21  :  [0, 250, 109],
     dom22  :  [58, 144, 255],
     dom23  :  [238, 130, 238] 
}


tint_factor = 0.5
tinted_colours = {} #new dictionary

def tint_colours(dict): #takes value for each RGB in each colour and tints it
    count = 1
    for keys, values in dict.items():
        #print(keys)
        tinted_list = []
        #print(values)
        for value in values:
            tinted_list.append(value + (255 - value)*tint_factor)
        tinted_colours["tint_dom" + str(count)] = tinted_list
        count += 1
    return tinted_colours



pprint.pprint(tint_colours(dict_of_colours))