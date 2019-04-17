from typing import List


class PhotoIdentification:
    kind = ''
    imprint = ''
    score = ''
    strength = ''
    colour = ''
    sizeDimensions = ''
    imageEncoding = ''

    def __init__(self, kind, imprint, score, strength, colour, sizeDimensions, imageencoding):
        self.kind = kind
        self.imprint = imprint
        self.score = score
        self.strength = strength
        self.colour = colour
        self.sizeDimensions = sizeDimensions
        self.imageEncoding = imageencoding


class PillData:
    def __init__(self, photofeatures: List[PhotoIdentification], pillname: str, substance: str):
        self.pillname = pillname
        self.substance = substance
        self.photofeatures: List[PhotoIdentification] = photofeatures
