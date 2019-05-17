from typing import List, Dict
from dataclasses import dataclass


@dataclass
class PillFeature():
    #pill: Dict
    name: str
    side: str
    kind: str
    strength: str
    shapefeature: List[float]
    colorfeature: List[str]