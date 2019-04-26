from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000

from source.fx.colorx.colormap import _map_rgb_color_to_xterm_color, convert_pixel_colors_to_vector

test_rgb = sRGBColor(128, 0, 0, is_upscaled=True)
test_data = [sRGBColor(128, 0, 0, is_upscaled=True), sRGBColor(0, 128, 0, is_upscaled=True), sRGBColor(238, 238, 238, is_upscaled=True)]


def test_mapping_rgb_to_lab():
    result = _map_rgb_color_to_xterm_color(test_rgb)
    assert result[1] == 1
    

def test_map_lab_to_vector():
    result = convert_pixel_colors_to_vector(test_data)
    assert result[1] == 1
    assert result[2] == 1
    assert result[255] == 1
