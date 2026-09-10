from PIL import Image, ImageDraw

SIZE = 512
BG = "#6E4A9E"
LILAC = "#DCCCF2"
MINT = "#DDF4EA"
TURQ = "#43B9A8"
GOLD = "#D6AD55"
GOLD_DARK = "#8F6B1E"
WHITE = "#FFFDFC"
INK = "#4E3474"


def tooth_polygon(cx, cy, scale=1.0):
    pts = [
        (cx-74*scale, cy-76*scale),
        (cx-48*scale, cy-100*scale),
        (cx-18*scale, cy-90*scale),
        (cx, cy-68*scale),
        (cx+18*scale, cy-90*scale),
        (cx+48*scale, cy-100*scale),
        (cx+74*scale, cy-76*scale),
        (cx+70*scale, cy-34*scale),
        (cx+52*scale, cy+8*scale),
        (cx+38*scale, cy+56*scale),
        (cx+24*scale, cy+104*scale),
        (cx+6*scale, cy+80*scale),
        (cx-6*scale, cy+80*scale),
        (cx-24*scale, cy+104*scale),
        (cx-38*scale, cy+56*scale),
        (cx-52*scale, cy+8*scale),
        (cx-70*scale, cy-34*scale),
    ]
    return [(int(x), int(y)) for x, y in pts]


def draw_brand(path_png="desktop/yomceph_logo.png", path_ico="desktop/yomceph.ico"):
    im = Image.new("RGBA", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(im)

    # Soft lilac halo for contrast at small icon sizes.
    d.ellipse((42, 42, 470, 470), fill=LILAC)
    d.ellipse((72, 72, 440, 440), fill="#F7F1FB")

    # Two stylised molars.
    for cx, cy, s, fill in [(190, 265, 0.93, WHITE), (322, 262, 0.93, MINT)]:
        poly = tooth_polygon(cx, cy, s)
        d.polygon(poly, fill=fill)
        d.line(poly + [poly[0]], fill=INK, width=12, joint="curve")

    # Turquoise measurement line between teeth, with end caps/ticks.
    d.line((145, 170, 365, 170), fill=TURQ, width=14)
    d.line((145, 150, 145, 190), fill=TURQ, width=10)
    d.line((365, 150, 365, 190), fill=TURQ, width=10)
    for x in range(175, 351, 35):
        d.line((x, 158, x, 182), fill=TURQ, width=7)

    # Gold set-square (escuadra) crossing the two teeth.
    tri = [(155, 335), (350, 335), (350, 205)]
    d.polygon(tri, fill=GOLD)
    d.line(tri + [tri[0]], fill=GOLD_DARK, width=12, joint="curve")
    inner = [(205, 310), (320, 310), (320, 236)]
    d.polygon(inner, fill="#F7F1FB")
    d.line(inner + [inner[0]], fill=GOLD_DARK, width=7, joint="curve")

    # Small drafting accents.
    d.ellipse((166, 321, 184, 339), fill=INK)
    d.ellipse((334, 321, 352, 339), fill=INK)

    im.save(path_png)
    im.save(path_ico, format="ICO", sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])


if __name__ == "__main__":
    draw_brand()
