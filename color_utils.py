import colorsys


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def rgb_to_hsl(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (round(h * 360), round(s * 100), round(l * 100))


def hsl_to_rgb(hsl):
    h, s, l = hsl
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return tuple(round(x * 255) for x in (r, g, b))


def get_luminance(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    return 0.299 * r + 0.587 * g + 0.114 * b


def get_contrast_color(rgb):
    return "#000000" if get_luminance(rgb) > 0.5 else "#ffffff"


def generate_shades(hex_color, count=5):
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(rgb)
    shades = []
    step = 80 / (count + 1)
    for i in range(1, count + 1):
        new_l = max(5, min(95, 10 + i * step))
        shade_rgb = hsl_to_rgb((h, s, new_l))
        shades.append(rgb_to_hex(shade_rgb))
    return shades


def generate_complementary(hex_color):
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(rgb)
    comp_h = (h + 180) % 360
    comp_rgb = hsl_to_rgb((comp_h, s, l))
    return rgb_to_hex(comp_rgb)


def generate_analogous(hex_color, count=4):
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(rgb)
    colors = []
    offsets = [-30, -15, 15, 30][:count]
    for offset in offsets:
        new_h = (h + offset) % 360
        new_rgb = hsl_to_rgb((new_h, s, l))
        colors.append(rgb_to_hex(new_rgb))
    return colors


def generate_triadic(hex_color):
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(rgb)
    colors = []
    for offset in [120, 240]:
        new_h = (h + offset) % 360
        new_rgb = hsl_to_rgb((new_h, s, l))
        colors.append(rgb_to_hex(new_rgb))
    return colors


def generate_monochromatic(hex_color, count=5):
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(rgb)
    colors = []
    lightness_values = [20, 35, 50, 65, 80][:count]
    for new_l in lightness_values:
        new_rgb = hsl_to_rgb((h, s, new_l))
        colors.append(rgb_to_hex(new_rgb))
    return colors


def is_valid_hex(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return False
    try:
        int(hex_color, 16)
        return True
    except ValueError:
        return False