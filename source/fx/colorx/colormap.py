import sys

from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from . import lab_objects


# Keep this method, just in case....
#
#def convert():
    # for color in hex_colors:
    #     # First convert HEX to RGB and store it in sRGBColor object
    #     rgb = sRGBColor.new_from_rgb_hex(color)

    #     # Convert sRGBColor object to L.a.b object
    #     converted_color = convert_color(rgb, LabColor)

    #     # Appending converted_color (LabColor object) to lab_objects list
    #     lab_objects.append(converted_color)
    
#    print(len(lab_objects))


def _map_rgb_color_to_xterm_color(srgb: sRGBColor):
    # Convert sRGBColor to L.a.b color object
    labcolor = convert_color(srgb, LabColor)

    # Find the color from lab_object that is most similar to labcolor
    lowest_d_val = sys.maxsize
    position_d_val = sys.maxsize

    position = 0
    for obj in lab_objects:
        delta_e = delta_e_cie2000(labcolor, obj)
        if delta_e < lowest_d_val:
            lowest_d_val = delta_e 
            position_d_val = position
            
        position = position + 1

    return lowest_d_val, position_d_val


def convert_pixel_colors_to_vector(pixel_array: []):
    """Expects a sRGBColor object as input. Use
    'from colormath.color_objects import sRGBColor' to create 
    sRGBColor object.
    """
    # instantiating an array of langth 256, to hold every color
    color_vector = [0 for x in range(256)]

    for color in pixel_array:
        result = _map_rgb_color_to_xterm_color(color)
        color_vector[result[1]] += 1

    return color_vector 
        
