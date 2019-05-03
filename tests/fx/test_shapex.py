import pytest
import sys
import numpy as np
import random as rng

# Import ShapePreprocessor file
sys.path.insert(0, 'source/fx')
from shapex import ShapePreprocessor
from shapex import ShapeDescriptor

########### ShapeProcessor tests below #############
shape_preprocessor = ShapePreprocessor()
img = shape_preprocessor.load_image_from_file("tests/images/pilltest1.jpg")

# Test load_image_from_file function - on error and success
def test_load_image_from_file_on_error():
    with pytest.raises(Exception) as e_inf:
        shape_preprocessor.load_image_from_file("")

def test_load_image_from_file_on_success():
    result = shape_preprocessor.load_image_from_file("tests/images/pilltest1.jpg")
    assert type(result) == np.ndarray

# Test crop_image function - on error and success
def test_crop_image_on_success_returns_two_images():
    crop_left, crop_right = shape_preprocessor.crop_image(img)

    assert type(crop_left) == np.ndarray
    assert type(crop_right) == np.ndarray

def test_crop_image_on_error_raises_exception():
    with pytest.raises(Exception) as e_inf:
        _, _ = shape_preprocessor.crop_image("")

# Test get_contours function - on success and on error
def test_get_contours_on_success():
    crop_left, crop_right = shape_preprocessor.crop_image(img)
    approx, edges, hierarchy = shape_preprocessor.get_contours(crop_left)

    assert len(approx) >= 0
    assert len(edges) >= 0
    assert len(hierarchy) != 0

def test_get_contours_on_error_raises_exception():
    with pytest.raises(Exception):
        _, _, _ = shape_preprocessor.get_contours(img)


############ ShapeDescriptor test below ################
shape_descriptor = ShapeDescriptor()
img = shape_preprocessor.load_image_from_file("tests/images/pilltest1.jpg")

# Test shape_descriptor constructor function
def test_shape_preprocessor_initialised_on_construct():
    assert type(shape_descriptor.preprocessor) == type(ShapePreprocessor())

# Test calc_hu_moments_from_image function - on success and error
def test_calc_hu_moments_from_image_on_success():
    fst_hu, snd_hu = shape_descriptor.calc_hu_moments_from_img(img)

    assert len(fst_hu) == 7
    assert len(snd_hu) == 7

def test_Calc_hu_moments_from_image_on_error():
    with pytest.raises(Exception) as e_inf: 
        shape_descriptor.calc_hu_moments_from_img("")

# Test calc_hu_moments on success and error
def test_calc_hu_moments_on_success():
    test_img, _ = shape_preprocessor.crop_image(img)
    _, edges, _ = shape_preprocessor.get_contours(test_img)
    hu_moments = shape_descriptor.calc_hu_moments(edges)

    assert len(hu_moments) == 7

def test_calc_hu_moments_on_error():
    with pytest.raises(Exception) as e_inf:
        _ = shape_descriptor.calc_hu_moments([])

# Test calc_cosine_similarity function - on error and success
def test_calc_cosine_similarity_on_success():
    fst_hu, snd_hu = shape_descriptor.calc_hu_moments_from_img(img)

    assert shape_descriptor.calc_cosine_similarity(fst_hu, snd_hu) >= 0

def test_calc_cosine_similarity_on_error():
    with pytest.raises(Exception) as e_inf:
        calc_cosine_similarity([1, 2], [])