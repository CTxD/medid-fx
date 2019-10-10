import os

from source.fx.colorx import pillcolorpixels


def test_getcolorpixels_mock_pill_photo():
    mockimagepath = os.path.join(os.getcwd(), 'tests', 'fx', 'mock_pill.png')
    result = pillcolorpixels.getcolorpixels(imagepath=mockimagepath)

    # Non-empty list
    assert isinstance(result, list) and result

    within = 0

    for pixel in result:
        rgb = pixel.get_upscaled_value_tuple()
        if rgb[0] > 240 and 130 < rgb[1] < 160 and rgb[2] > 240:
            within += 1
    
    assert len(result)/100*70 < within