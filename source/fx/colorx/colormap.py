import sys
from typing import Dict

from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000, delta_e_cie1976, delta_e_cie1994
from . import six_bit_lab, six_bit_hex, eight_bit_lab, eight_bit_hex

hex_values = {
    6: six_bit_hex,
    8: eight_bit_hex
}

lab_objects = {
    6: six_bit_lab,
    8: eight_bit_lab
}

delta_algorithms = {
    1976: delta_e_cie1976,
    1994: delta_e_cie1994,
    2000: delta_e_cie2000
}

# lab_objects = eight_bit_lab
# hex_values = eight_bit_hex

# Keep this method, just in case....
#
# def convert(bit: int):
#     lab_objects = []
#     for color in six_bit_hex:
#         # First convert HEX to RGB and store it in sRGBColor object
#         rgb = sRGBColor.new_from_rgb_hex(color)

#         # Convert sRGBColor object to L.a.b object
#         converted_color = convert_color(rgb, LabColor)

#         # Appending converted_color (LabColor object) to lab_objects list
#         lab_objects.append(converted_color)
    
#     print(lab_objects)

#     exit()


def _map_rgb_color_to_xterm_color(srgb: sRGBColor, bit: int, delta_e: int):
    # Convert sRGBColor to L.a.b color object
    labcolor = convert_color(srgb, LabColor)

    # Find the color from lab_object that is most similar to labcolor
    lowest_d_val = sys.maxsize
    position_d_val = sys.maxsize

    position = 0
    for obj in lab_objects[bit]:
        delta_value = delta_algorithms[delta_e](labcolor, obj)
        if delta_value < lowest_d_val:
            lowest_d_val = delta_value 
            position_d_val = position
            
        position = position + 1

    return lowest_d_val, position_d_val
 

def convert_pixel_colors_to_vector(hexcount: Dict[str, int], bit: int, delta_e: int):
    """Expects a dictionary of hex values and corresponding count as input. """
    # instantiating an array of langth 256, to hold every color
    color_vector = [0 for x in range(len(hex_values[bit]))]
    for hexvalue, count in hexcount.items():
        color = sRGBColor.new_from_rgb_hex(hexvalue)
        result = _map_rgb_color_to_xterm_color(color, bit, delta_e)
        color_vector[result[1]] += count # noqa

    return {hex_values[bit][index]: color_vector[index] for index in range(0, len(hex_values[bit]))}
        
