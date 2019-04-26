from colormath.color_objects import sRGBColor
from source.fx.colorx.colormap import _map_rgb_color_to_xterm_color

def main():
    print(_map_rgb_color_to_xterm_color(sRGBColor(66, 134, 244, is_upscaled=True)))
   