def imgsplitgenerator(imageencoding: str):
    """
    Given an encoding of a pro.medicin.dk image, this function will create an image of the encoding,
    split it and create 2 temporary files, one for each of the pill sides. It will then yield the
    path to these images (left first, then right). 

    NOTE: The temp images will be destroyed once the generator finished. The 
    """
    pass
#     with encoding2img.Encoding2IMG(base64.b64encode(f.read())) as tmpimgpath:
#         left, right = ShapePreprocessor().crop_image(tmpimgpath, grayscale=False)
#         tmpimgname, tmpimgext = os.path.basename(tmpimgpath).split('.')
#         tmpimgpath = os.path.dirname(tmpimgpath)
#         leftimgpath = os.path.join(tmpimgpath, f'{tmpimgname}_left.{tmpimgext}')
#         rightimgpath = os.path.join(tmpimgpath, f'{tmpimgname}_right.{tmpimgext}')
#         cv.imwrite(leftimgpath, cv.cvtColor(left, cv.COLOR_RGB2BGRA))
#         cv.imwrite(rightimgpath, cv.cvtColor(right, cv.COLOR_RGB2BGRA))
#         yield leftimgpath
#         yield rightimgpath