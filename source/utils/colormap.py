from PIL import Image
from PIL import ImageDraw

from colormath.color_objects import sRGBColor
import math


test = [
    sRGBColor(128, 0, 0, is_upscaled=True), sRGBColor(0, 128, 0, is_upscaled=True), 
    sRGBColor(128, 0, 0, is_upscaled=True), sRGBColor(0, 128, 0, is_upscaled=True),
    sRGBColor(128, 0, 0, is_upscaled=True), sRGBColor(0, 128, 0, is_upscaled=True),
    sRGBColor(128, 0, 0, is_upscaled=True), sRGBColor(0, 128, 0, is_upscaled=True),
    sRGBColor(128, 0, 0, is_upscaled=True), sRGBColor(0, 128, 0, is_upscaled=True),
    sRGBColor(128, 0, 0, is_upscaled=True), sRGBColor(0, 128, 0, is_upscaled=True),
    sRGBColor(238, 238, 238, is_upscaled=True)
]


def main():
    img_creater(test, 50, "test")


def img_creater(array_of_colors: [sRGBColor], size: int, filename: str):
    i = math.ceil(math.sqrt(len(array_of_colors)))
    
    img = Image.new("RGBA", (i*size, i*size), color='black')
    draw = ImageDraw.Draw(img)

    x1 = 0
    x2 = 0
    y1 = size
    y2 = size

    array_of_colors.sort(key=lambda x: (x.rgb_r, x.rgb_g, x.rgb_b))

    counter = 0
    for color in array_of_colors:
        
        c = color.get_rgb_hex()

        draw.rectangle(((0+x1, x2), ((size+y1, y2))), fill=c)
        x1 += size
        y1 += size

        counter += 1

        if counter >= i:
            x1 = 0
            x2 += size
            y1 = size
            y2 += size
            counter = 0
        
    img.save(filename + ".png")