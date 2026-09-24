import math, random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

import os

# Bangers.ttf is not committed to this repo. Download it from
# https://fonts.google.com/specimen/Bangers and drop it next to this script.
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "puzzle")
pdfmetrics.registerFont(TTFont("Bangers", os.path.join(HERE, "Bangers.ttf")))

W, _ = letter
H = 900  # recomputed in draw()
RED = HexColor("#D62828")
BLUE = HexColor("#1D3557")
SKY = HexColor("#A8DADC")
YEL = HexColor("#FFD60A")
INK = HexColor("#111111")
PAPER = HexColor("#FFFDF5")
GREY = HexColor("#9A9A9A")

# ---------- emblems ----------
def poly(c, pts, fill=INK):
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    c.setFillColor(fill)
    c.drawPath(p, stroke=0, fill=1)

def em_shield(c, x, y, s, col):
    p = c.beginPath()
    p.moveTo(x - s*.75, y + s*.8)
    p.lineTo(x + s*.75, y + s*.8)
    p.curveTo(x + s*.8, y - s*.1, x + s*.5, y - s*.6, x, y - s*.95)
    p.curveTo(x - s*.5, y - s*.6, x - s*.8, y - s*.1, x - s*.75, y + s*.8)
    p.close()
    c.setFillColor(col); c.drawPath(p, stroke=0, fill=1)
    c.setStrokeColor(white); c.setLineWidth(s*.12)
    c.line(x, y + s*.6, x, y - s*.65)

def em_mask(c, x, y, s, col):
    p = c.beginPath()
    p.moveTo(x - s, y + s*.15)
    p.curveTo(x - s*.9, y + s*.65, x - s*.3, y + s*.55, x, y + s*.3)
    p.curveTo(x + s*.3, y + s*.55, x + s*.9, y + s*.65, x + s, y + s*.15)
    p.curveTo(x + s*.95, y - s*.45, x + s*.3, y - s*.55, x, y - s*.2)
    p.curveTo(x - s*.3, y - s*.55, x - s*.95, y - s*.45, x - s, y + s*.15)
    p.close()
    c.setFillColor(col); c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(white)
    c.ellipse(x - s*.68, y - s*.18, x - s*.22, y + s*.22, stroke=0, fill=1)
    c.ellipse(x + s*.22, y - s*.18, x + s*.68, y + s*.22, stroke=0, fill=1)

def em_target(c, x, y, s, col):
    c.setFillColor(col); c.circle(x, y, s*.95, stroke=0, fill=1)
    c.setFillColor(white); c.circle(x, y, s*.68, stroke=0, fill=1)
    c.setFillColor(col); c.circle(x, y, s*.42, stroke=0, fill=1)
    c.setFillColor(white); c.circle(x, y, s*.16, stroke=0, fill=1)

def em_crescent(c, x, y, s, col, bg=white):
    c.setFillColor(col); c.circle(x, y, s*.9, stroke=0, fill=1)
    c.setFillColor(bg); c.circle(x + s*.4, y + s*.25, s*.75, stroke=0, fill=1)

def em_bat(c, x, y, s, col):
    pts = [(-1.0, .25), (-.55, .45), (-.3, .3), (-.15, .5), (-.08, .32), (0, .38),
           (.08, .32), (.15, .5), (.3, .3), (.55, .45), (1.0, .25),
           (.75, .05), (.7, -.2), (.45, -.08), (.3, -.35), (.12, -.2), (0, -.5),
           (-.12, -.2), (-.3, -.35), (-.45, -.08), (-.7, -.2), (-.75, .05)]
    poly(c, [(x + a*s, y + b*s) for a, b in pts], col)

def em_bolt(c, x, y, s, col):
    pts = [(.25, 1), (-.55, -.1), (-.05, -.1), (-.3, -1), (.55, .15), (.05, .15), (.35, 1)]
    poly(c, [(x + a*s, y + b*s*.95) for a, b in pts], col)

def em_star(c, x, y, s, col):
    pts = []
    for i in range(10):
        r = s * (1 if i % 2 == 0 else .42)
        a = math.pi/2 + i * math.pi/5
        pts.append((x + r*math.cos(a), y + r*math.sin(a) - s*.08))
    poly(c, pts, col)

def em_diamond(c, x, y, s, col):
    poly(c, [(x - s*.9, y + s*.3), (x - s*.5, y + s*.75), (x + s*.5, y + s*.75),
             (x + s*.9, y + s*.3), (x, y - s*.9)], col)
    c.setStrokeColor(white); c.setLineWidth(s*.08)
    c.line(x - s*.9, y + s*.3, x + s*.9, y + s*.3)
    c.line(x - s*.25, y + s*.3, x, y - s*.9)
    c.line(x + s*.25, y + s*.3, x, y - s*.9)

EMBLEMS = {"shield": em_shield, "mask": em_mask, "target": em_target, "crescent": em_crescent,
           "bat": em_bat, "bolt": em_bolt, "star": em_star, "diamond": em_diamond}

def badge(c, name, x, y, r, col=BLUE):
    c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(1.6)
    c.circle(x, y, r, stroke=1, fill=1)
    EMBLEMS[name](c, x, y, r*.62, col)

# ---------- puzzle data ----------
ROWS = [  # clue, jumble, word, extra, emblem
    ("Not all heroes wear these", "EPRCAS", "CAPES", "R", "shield"),
    ("It keeps a secret identity secret", "SAMAK", "MASK", "A", "mask"),
    ("Shone into the night sky to call for help", "GLAKNIS", "SIGNAL", "K", "target"),
    ("Twirls a mustache, monologues too long", "LAVILEIN", "VILLAIN", "E", "crescent"),
    ("\u201cUp, up, and away!\u201d", "THGLIDF", "FLIGHT", "D", "bat"),
    ("Stretchy legwear, often under the trunks", "HUGTTIS", "TIGHTS", "U", "bolt"),
    ("______ story: how it all began", "GIRSONI", "ORIGIN", "S", "star"),
    ("Green rock from a doomed planet", "TORYNICKTEP", "KRYPTONITE", "C", "diamond"),
]
ANSWER = "CAKED CRUSADER"
HOST = "Captain Birthday"
FLAVOR = (f"{HOST} is planning a party. All of his superhero friends are changing into their "
          "costumes to celebrate. Every hero ducked into a phone booth to change, but "
          "<b>each came out with a little something extra</b>. Before sending out the invites, "
          f"{HOST} realized he had one last birthday superhero to add to the guest list. Who was it?")
CAP_STYLE = ParagraphStyle("cap", fontName="Helvetica", fontSize=12.5, leading=17,
                           textColor=HexColor("#111111"), alignment=TA_LEFT)
for clue, jum, word, extra, emb in ROWS:
    assert sorted(jum) == sorted(word + extra), (jum, word)
    assert jum[0] != extra and jum[-1] != extra, jum
EMB_FOR = {r[3]: r[4] for r in ROWS}

def halftone(c, x0, y0, x1, y1, col, step=9, rmax=2.6, fade="right"):
    c.setFillColor(col)
    y = y0
    row = 0
    while y < y1:
        x = x0 + (step/2 if row % 2 else 0)
        while x < x1:
            t = (x - x0) / (x1 - x0)
            r = rmax * (t if fade == "right" else 1 - t)
            if r > .3:
                c.circle(x, y, r, stroke=0, fill=1)
            x += step
        y += step; row += 1

def burst(c, x, y, r1, r2, n, col, seed=3):
    rnd = random.Random(seed)
    pts = []
    for i in range(n*2):
        a = i * math.pi / n
        r = (r1 if i % 2 == 0 else r2) * (1 + rnd.uniform(-.08, .08))
        pts.append((x + r*math.cos(a), y + r*math.sin(a)))
    p = c.beginPath(); p.moveTo(*pts[0])
    for pt in pts[1:]: p.lineTo(*pt)
    p.close()
    c.setFillColor(col); c.setStrokeColor(INK); c.setLineWidth(2)
    c.drawPath(p, stroke=1, fill=1)

def draw(path, key=False):
    global H
    _, ph = Paragraph(FLAVOR, CAP_STYLE).wrap(W - 2*36 - 60 - 32, 1000)
    H = 36 + 118 + 14 + (ph + 26) + 16 + 10 + 8*47 + 22 + 98 + 44
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Quick Change - Location Puzzle" + (" (Answer Key)" if key else ""))
    c.setFillColor(PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)

    M = 36
    # ---- header panel ----
    top = H - M
    hh = 118
    c.setFillColor(SKY); c.setStrokeColor(INK); c.setLineWidth(3)
    c.rect(M, top - hh, W - 2*M, hh, stroke=1, fill=1)
    halftone(c, M + 4, top - hh + 4, W - M - 4, top - 4, HexColor("#6FB7C0"))
    burst(c, W - M - 78, top - hh/2 - 2, 60, 44, 14, YEL)
    c.setFillColor(RED); c.setFont("Bangers", 22)
    c.drawCentredString(W - M - 78, top - hh/2 + 4, "LOCATION")
    c.drawCentredString(W - M - 78, top - hh/2 - 18, "PUZZLE")
    # title with drop shadow
    c.setFont("Bangers", 64)
    c.setFillColor(INK); c.drawString(M + 22 + 4, top - 76 - 4, "QUICK CHANGE!")
    c.setFillColor(RED); c.drawString(M + 22, top - 76, "QUICK CHANGE!")
    c.setFillColor(BLUE); c.setFont("Bangers", 17)
    c.drawString(M + 24, top - 102, "A SUPERHERO PUZZLE HUNT")

    # ---- caption box (flavor text) ----
    cy = top - hh - 14
    cw = W - 2*M - 60
    para = Paragraph(FLAVOR, CAP_STYLE)
    _, ph = para.wrap(cw - 32, 1000)
    ch = ph + 26
    c.setFillColor(YEL); c.setStrokeColor(INK); c.setLineWidth(2)
    c.rect(M + 30, cy - ch, cw, ch, stroke=1, fill=1)
    para.drawOn(c, M + 46, cy - 13 - ph)

    # ---- clue rows ----
    y = cy - ch - 16
    rh = 47
    x_badge, x_clue, x_ans, x_extra = M + 22, M + 52, 332, W - M - 22
    c.setFont("Bangers", 13); c.setFillColor(BLUE)
    c.drawString(x_clue, y - 2, "CLUE  /  WHAT CAME OUT OF THE BOOTH")
    c.drawString(x_ans, y - 2, "WHAT WENT IN")
    c.drawCentredString(x_extra, y - 2, "EXTRA")
    y -= 10
    for i, (clue, jum, word, extra, emb) in enumerate(ROWS):
        ry = y - i*rh
        if i % 2 == 0:
            c.setFillColor(HexColor("#F3EFE2"))
            c.rect(M, ry - rh, W - 2*M, rh, stroke=0, fill=1)
        mid = ry - rh/2
        badge(c, emb, x_badge, mid, 16)
        c.setFillColor(INK); c.setFont("Helvetica", 11)
        c.drawString(x_clue, mid + 9, clue)
        # jumble tiles
        tw = 18
        for j, ch_ in enumerate(jum):
            tx = x_clue + j*(tw + 2)
            c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(1.2)
            c.rect(tx, mid - 17, tw, tw, stroke=1, fill=1)
            c.setFillColor(INK); c.setFont("Bangers", 15)
            c.drawCentredString(tx + tw/2, mid - 12.5, ch_)
        # answer blanks
        bw = 15
        for j in range(len(word)):
            bx = x_ans + j*(bw + 3)
            c.setStrokeColor(INK); c.setLineWidth(1.4)
            c.line(bx, mid - 8, bx + bw, mid - 8)
            if key:
                c.setFillColor(RED); c.setFont("Bangers", 17)
                c.drawCentredString(bx + bw/2, mid - 5, word[j])
        # extra box
        c.setFillColor(YEL); c.setStrokeColor(INK); c.setLineWidth(2)
        c.rect(x_extra - 14, mid - 14, 28, 28, stroke=1, fill=1)
        if key:
            c.setFillColor(RED); c.setFont("Bangers", 20)
            c.drawCentredString(x_extra, mid - 7, extra)
    c.setStrokeColor(INK); c.setLineWidth(1)
    c.rect(M, y - len(ROWS)*rh, W - 2*M, len(ROWS)*rh, stroke=1, fill=0)

    # ---- final answer strip ----
    fy = y - len(ROWS)*rh - 22
    fh = 98
    c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(3)
    c.rect(M, fy - fh, W - 2*M, fh, stroke=1, fill=1)
    halftone(c, M + 4, fy - fh + 4, W - M - 4, fy - 4, HexColor("#F4C7C7"), fade="left")
    c.setFillColor(RED); c.setFont("Bangers", 20)
    c.drawCentredString(W/2, fy - 24, "WHO STILL NEEDS AN INVITE?")
    bs, gap, wgap = 28, 5, 22
    n = len(ANSWER.replace(" ", ""))
    total = n*bs + (n - 2)*gap + wgap
    bx = W/2 - total/2
    by = fy - 66
    for ch_ in ANSWER:
        if ch_ == " ":
            bx += wgap - gap
            continue
        c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(2)
        c.rect(bx, by, bs, bs, stroke=1, fill=1)
        if key:
            c.setFillColor(RED); c.setFont("Bangers", 22)
            c.drawCentredString(bx + bs/2, by + 7, ch_)
        EMBLEMS[EMB_FOR[ch_]](c, bx + bs/2, by - 16, 9, BLUE) if EMB_FOR[ch_] != "crescent" \
            else em_crescent(c, bx + bs/2, by - 16, 9, BLUE, bg=HexColor("#FBEAEA"))
        bx += bs + gap

    c.setFillColor(GREY); c.setFont("Helvetica-Oblique", 8.5)
    c.drawCentredString(W/2, M - 20, "Answer Key" if key else "Solve it, then go find it.")
    c.save()

draw(os.path.join(OUT, "quick-change.pdf"))
draw(os.path.join(OUT, "quick-change-answer-key.pdf"), key=True)
print("ok")
