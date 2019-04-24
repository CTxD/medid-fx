from .colormap import map_hex_color_to_xterm_color


def main():
    res = map_hex_color_to_xterm_color("#f97924")

    print(res)
