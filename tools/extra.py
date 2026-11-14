import os
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""Extra creatives: daily stories (1080x1920), highlight covers, ad sets, YouTube thumbnails."""
import json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
from plan import Q
OUT = os.path.join(ROOT,'media')
CR = os.path.join(ROOT,'creatives')
for d_ in ('story', 'thumb'): os.makedirs(f'{OUT}/{d_}', exist_ok=True)
for d_ in ('highlight', 'ads'): os.makedirs(f'{CR}/{d_}', exist_ok=True)
days = json.load(open(os.path.join(ROOT,'content','plan.json')))
SW, SH = 1080, 1920
LABEL = {1: 'The lawn', 2: 'The pool', 3: "Kids' pool", 4: 'Pool deck', 5: 'The porch', 6: 'Lawn view', 7: 'The terrace', 8: 'Sundowner deck'}

def cta(c, y):
    d = ImageDraw.Draw(c); t = 'DM “DATE”  ·  +91 78277 13708'; f = PS(36, 'SemiBold')
    w = d.textlength(t, font=f) + 90
    d.rounded_rectangle((SW / 2 - w / 2, y, SW / 2 + w / 2, y + 96), radius=48, fill=CH + (255,))
    d.text((SW / 2 - d.textlength(t, font=f) / 2, y + 26), t, font=f, fill=DEEP)

def centered(d, y, text, f, fill, lh=1.15, maxw=SW - 160, maxl=3, mk=None, size=None):
    if mk: f, L = fitwrap(d, text, mk, size, maxw, maxl, 40)
    else: L = wrap(d, text, f, maxw)
    for l in L:
        d.text((SW / 2 - d.textlength(l, font=f) / 2, y), l, font=f, fill=fill); y += int(f.size * lh)
    return y

def story(x):
    k = x['qi'] % 3; p = x['photo']
    if k == 0:  # feature
        c = fit(photo(p), SW, SH, 0.5, 0.5).convert('RGBA')
        c.alpha_composite(grad_cached((SW, SH), 0, 1150, 225, 0)); c.alpha_composite(grad_cached((SW, SH), 1250, 1920, 0, 235))
        d = ImageDraw.Draw(c); c.alpha_composite(logo(110), (SW // 2 - 55, 150))
        spaced(d, (SW / 2, 300), x['kicker'].upper(), PS(34, 'SemiBold'), CH, 6, 'm')
        y = centered(d, 370, x['head'], None, CREAM, mk=PF, size=110)
        if x['en']: centered(d, y + 20, x['en'], None, SOFT, 1.4, maxl=2, mk=PS, size=40)
        centered(d, 1500, 'Today on our feed', PI(44), CH); cta(c, 1600)
    elif k == 1:  # this or that
        q = Q['day'][x['qi'] % len(Q['day'])] if x['typ'] not in Q else Q[x['typ']][x['qi'] % len(Q[x['typ']])]
        a, b = p, (p + 2) % 8 + 1
        c = Image.new('RGBA', (SW, SH), DEEP + (255,))
        c.paste(fit(photo(a), SW, 820), (0, 0)); c.paste(fit(photo(b), SW, 820), (0, 1100))
        d = ImageDraw.Draw(c)
        for (yy, lab) in ((700, LABEL[a]), (1800, LABEL[b])):
            f = PS(34, 'SemiBold'); w = d.textlength(lab, font=f) + 60
            d.rounded_rectangle((SW / 2 - w / 2, yy, SW / 2 + w / 2, yy + 70), radius=35, fill=DEEP + (225,))
            d.text((SW / 2 - d.textlength(lab, font=f) / 2, yy + 14), lab, font=f, fill=CREAM)
        centered(d, 860, q, None, CREAM, mk=PF, size=64, maxl=2)
        centered(d, 1030, 'Reply to this story — we read every message', PS(30), CH)
    else:  # tip card
        c = fit(photo(p), SW, SH).filter(ImageFilter.GaussianBlur(14)).convert('RGBA')
        c.alpha_composite(Image.new('RGBA', (SW, SH), DEEP + (90,)))
        d = ImageDraw.Draw(c); d.rounded_rectangle((80, 360, SW - 80, 1500), radius=40, fill=CREAM + (246,))
        spaced(d, (SW / 2, 430), x['kicker'].upper(), PS(30, 'SemiBold'), (150, 120, 60), 6, 'm')
        y = centered(d, 490, x['ptitle'], PF(80), NIGHT)
        y += 40
        for i, pt in enumerate(x['points'][:4]):
            d.ellipse((150, y, 226, y + 76), outline=CH, width=3)
            n = f'{i+1:02d}'; f = PF(34, 'Bold'); d.text((188 - d.textlength(n, font=f) / 2, y + 14), n, font=f, fill=NIGHT)
            f2, L = fitwrap(d, pt, PS, 40, SW - 420, 2, 28); yy = y + (76 - len(L) * int(f2.size * 1.3)) // 2
            for l in L: d.text((256, yy), l, font=f2, fill=INK); yy += int(f2.size * 1.3)
            y += 190
        cta(c, 1600)
    c.convert('RGB').save(f"{OUT}/story/{x['id']}.jpg", quality=90)

ICONS = ['Pool', 'Lawn', 'Weddings', 'Birthdays', 'Corporate', 'Stays', 'Reviews', 'Contact']
def icon(d, name, cx, cy, s, col):
    w = 10
    if name == 'Pool':
        for k in range(3):
            pts = [(cx - s + i * 4, cy - s * 0.4 + k * s * 0.45 + math.sin(i / 10) * s * 0.12) for i in range(int(2 * s / 4) + 1)]
            d.line(pts, fill=col, width=w, joint='curve')
    elif name == 'Lawn':
        d.polygon([(cx, cy - s), (cx - s * 0.7, cy + s * 0.3), (cx + s * 0.7, cy + s * 0.3)], outline=col, width=w)
        d.line((cx, cy + s * 0.3, cx, cy + s), fill=col, width=w)
    elif name == 'Weddings':
        r = s * 0.45; d.ellipse((cx - r * 1.7, cy - r, cx + r * 0.3, cy + r), outline=col, width=w); d.ellipse((cx - r * 0.3, cy - r, cx + r * 1.7, cy + r), outline=col, width=w)
    elif name == 'Birthdays':
        d.rectangle((cx - s * 0.8, cy, cx + s * 0.8, cy + s * 0.8), outline=col, width=w); d.line((cx - s * 0.8, cy + s * 0.35, cx + s * 0.8, cy + s * 0.35), fill=col, width=w)
        for dx in (-0.45, 0, 0.45):
            d.line((cx + dx * s, cy - s * 0.1, cx + dx * s, cy - s * 0.55), fill=col, width=w); d.ellipse((cx + dx * s - 9, cy - s * 0.8, cx + dx * s + 9, cy - s * 0.6), fill=col)
    elif name == 'Corporate':
        d.rounded_rectangle((cx - s * 0.9, cy - s * 0.3, cx + s * 0.9, cy + s * 0.75), radius=14, outline=col, width=w)
        d.rounded_rectangle((cx - s * 0.35, cy - s * 0.65, cx + s * 0.35, cy - s * 0.3), radius=10, outline=col, width=w)
    elif name == 'Stays':
        d.ellipse((cx - s * 0.8, cy - s * 0.8, cx + s * 0.8, cy + s * 0.8), outline=col, width=w); d.ellipse((cx - s * 0.3, cy - s * 0.95, cx + s * 1.1, cy + s * 0.55), fill=DEEP)
    elif name == 'Reviews':
        pts = []
        for i in range(10):
            r = s if i % 2 == 0 else s * 0.42; a = -math.pi / 2 + i * math.pi / 5
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, outline=col, width=w)
    elif name == 'Contact':
        d.rounded_rectangle((cx - s * 0.5, cy - s * 0.9, cx + s * 0.5, cy + s * 0.9), radius=22, outline=col, width=w); d.line((cx - 18, cy + s * 0.65, cx + 18, cy + s * 0.65), fill=col, width=w)

def highlights():
    for name in ICONS:
        c = Image.new('RGB', (SW, SH), DEEP); d = ImageDraw.Draw(c)
        d.ellipse((SW / 2 - 300, SH / 2 - 300, SW / 2 + 300, SH / 2 + 300), outline=CH, width=8)
        icon(d, name, SW / 2, SH / 2 - 20, 150, CH)
        f = PS(44, 'SemiBold'); spaced(d, (SW / 2, SH / 2 + 360), name.upper(), f, CREAM, 8, 'm')
        c.save(f'{CR}/highlight/{name.lower()}.jpg', quality=92)

ADS = [
 ('birthday', 1, 'Birthday party, private pool', 'Your guests only. Lawn, pool and 3 bedrooms in Sector 135, Noida.'),
 ('haldi', 2, 'Haldi by a private pool', 'Lawn mandap, poolside splash, rooms to get ready. Up to 150 guests.'),
 ('corporate', 6, 'Offsite without the boardroom', 'Porch sessions, lawn lunch, team games. Beside the Noida Expressway.'),
 ('poolparty', 8, 'A pool party that is all yours', 'Private pool with a kids’ section, deck and music till 10 pm.'),
 ('family', 5, 'The whole farmhouse, one family', 'Lawn for 150, shaded porch, pool and 3 bedrooms for a stay-over.'),
]
def ad(slug, pid, head, sub, W_, H_):
    c = fit(photo(pid), W_, H_).convert('RGBA'); c.alpha_composite(grad_cached((W_, H_), int(H_ * 0.35), H_, 0, 240))
    d = ImageDraw.Draw(c); c.alpha_composite(logo(90), (50, 50))
    spaced(d, (160, 76), 'NOIDA FARMHOUSE PARTY', PS(24, 'SemiBold'), CREAM, 4)
    f, L = fitwrap(d, head, PF, 84 if W_ == H_ else 92, W_ - 140, 2, 50)
    f2, L2 = fitwrap(d, sub, PS, 34, W_ - 140, 2, 26)
    total = len(L) * int(f.size * 1.14) + 10 + len(L2) * int(f2.size * 1.4) + 24 + 84
    y = H_ - 70 - total - (140 if H_ == 1920 else 0)
    for l in L: d.text((70, y), l, font=f, fill=CREAM); y += int(f.size * 1.14)
    y += 10
    for l in L2: d.text((70, y), l, font=f2, fill=SOFT); y += int(f2.size * 1.4)
    y += 24; t = 'Get a quote'; fb = PS(34, 'SemiBold'); w = d.textlength(t, font=fb) + 80
    d.rounded_rectangle((70, y, 70 + w, y + 84), radius=42, fill=CH + (255,)); d.text((110, y + 20), t, font=fb, fill=DEEP)
    spaced(d, (70 + w + 30, y + 28), '+91 78277 13708', PS(28, 'SemiBold'), CREAM, 2)
    c.convert('RGB').save(f'{CR}/ads/{slug}_{W_}x{H_}.jpg', quality=92)

def thumb(x):
    TW, TH = 1280, 720
    c = Image.new('RGB', (TW, TH), DEEP); c.paste(fit(photo(x['photo']), 760, TH), (0, 0))
    d = ImageDraw.Draw(c); d.rectangle((760, 0, TW, TH), fill=DEEP)
    c.paste(logo(80), (800, 60), logo(80))
    spaced(d, (800, 180), x['kicker'].upper()[:26], PS(24, 'SemiBold'), CH, 4)
    f, L = fitwrap(d, x['head'], PF, 66, TW - 840, 4, 40); y = 230
    for l in L: d.text((800, y), l, font=f, fill=CREAM); y += int(f.size * 1.15)
    d.line((800, y + 20, 900, y + 20), fill=CH, width=3)
    d.text((800, TH - 90), 'Sector 135, Noida', font=PS(28, 'Medium'), fill=SOFT)
    c.save(f"{OUT}/thumb/{x['id']}.jpg", quality=90)

if __name__ == '__main__':
    for x in days: story(x); thumb(x)
    highlights()
    for slug, pid, h, s in ADS:
        for W_, H_ in ((1080, 1080), (1080, 1350), (1080, 1920)): ad(slug, pid, h, s, W_, H_)
    print('ok', len(os.listdir(f'{OUT}/story')), len(os.listdir(f'{OUT}/thumb')), len(os.listdir(f'{CR}/highlight')), len(os.listdir(f'{CR}/ads')))
