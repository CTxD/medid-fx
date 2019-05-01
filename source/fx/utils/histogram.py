from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt

from ..colorx import colormap


def createhistogram(colorcount: Dict[str, int], imagepath: str, bitcolor: int):
    colorbins = colormap.hex_values[bitcolor]

    values: List[float] = [
        colorcount[colorbins[index]] if colorbins[index] in colorcount else 0 
        for index in range(0, len(colorbins))
    ]
    
    # values = []
    # for index in range(0, len(colorbins)): # noqa
    #     color = colorbins[index]
    #     values.append(colorcount[color])    
    
    #     count = 0 if color not in colorcount else colorcount[color]
    #     values.append((1/total)*count*100)
    x = np.arange(len(colorbins))

    fig, ax = plt.subplots()
    ax.set_ylim(0, 100)
    r = plt.bar(x, values)
    for index in range(0, len(colorbins)): # noqa
        r.patches[index].set_fc('#'+colorbins[index])
        r.patches[index].set_ec('black')
    plt.xticks(x, [f'{colorbins.index(color)}: #' + color for color in colorbins], rotation=-60)

    fig.set_size_inches(20, 12)
    fig.savefig(imagepath, dpi=100, bbox_inches='tight')