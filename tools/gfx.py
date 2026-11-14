import os
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import functools
P = os.path.join(ROOT,'photos','Noida_Farmhouse_0%d.jpg')
F = os.path.join(ROOT,'fonts')+'/'
NIGHT = (31, 58, 47); DEEP = (18, 38, 30); CH = (227, 205, 157); CREAM = (251, 248, 242); INK = (28, 40, 34); SOFT = (226, 233, 228)
LOGO = os.path.join(ROOT,'assets','logo-nfp.jpg')

@functools.lru_cache(None)
def font(n, s, w=None):
    f = ImageFont.truetype(F + n, s)
    if w:
        try: f.set_variation_by_name(w)
        except Exception: pass
    return f
def PF(s, w='SemiBold'): return font('PlayfairDisplay[wght].ttf', s, w)
def PI(s): return font('PlayfairDisplay-Italic[wght].ttf', s, 'Medium')
def PS(s, k='Regular'): return font(f'Poppins-{k}.ttf', s)

@functools.lru_cache(None)
def photo(i): return Image.open(P % i).convert('RGB')

def fit(im, w, h, xb=0.5, yb=0.5):
    r = max(w / im.width, h / im.height); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = int((im.width - w) * xb); y = int((im.height - h) * yb); return im.crop((x, y, x + w, y + h))

def wrap(d, text, f, maxw):
    words = text.split(); lines = []; cur = ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fitwrap(d, text, mk, size, maxw, maxlines, minsize=30):
    while size >= minsize:
        f = mk(size); L = wrap(d, text, f, maxw)
        if len(L) <= maxlines: return f, L
        size -= 4
    f = mk(minsize); return f, wrap(d, text, f, maxw)

def spaced(d, xy, text, f, fill, sp=4, anchor='l'):
    x, y = xy
    tw = sum(d.textlength(c, font=f) for c in text) + sp * (len(text) - 1)
    if anchor == 'm': x -= tw / 2
    for c in text:
        d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp
    return tw

def grad(size, y0, y1, col, a0, a1, top=False):
    w, h = size; g = Image.new('RGBA', size, (0, 0, 0, 0)); px = g.load()
    for y in range(h):
        if top: t = 1 - min(1, max(0, (y - y0) / max(1, y1 - y0)))
        else: t = min(1, max(0, (y - y0) / max(1, y1 - y0)))
        a = int(a0 + (a1 - a0) * t)
        for x in range(w): px[x, y] = col + (a,)
    return g

@functools.lru_cache(None)
def grad_cached(size, y0, y1, a0, a1, top=False):
    # vertical gradient via 1px column resize (fast)
    w, h = size; col = Image.new('RGBA', (1, h))
    for y in range(h):
        if top: t = 1 - min(1, max(0, (y - y0) / max(1, y1 - y0)))
        else: t = min(1, max(0, (y - y0) / max(1, y1 - y0)))
        col.putpixel((0, y), DEEP + (int(a0 + (a1 - a0) * t),))
    return col.resize((w, h))

@functools.lru_cache(None)
def logo(sz):
    lg = Image.open(LOGO).convert('RGB').resize((sz, sz), Image.LANCZOS)
    m = Image.new('L', (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz - 1, sz - 1), fill=255)
    out = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); out.paste(lg, (0, 0), m); return out

def brandbar(c, y, light=True):
    d = ImageDraw.Draw(c); col = CH if light else NIGHT
    spaced(d, (c.width / 2, y), 'NOIDA FARMHOUSE PARTY  ·  SECTOR 135, NOIDA', PS(22, 'Medium'), col, 3, 'm')

# ---------- feed images (1080x1350) ----------
W, H = 1080, 1350

def cover(x, pid=None, swipe=False, yb=0.5):
    pid = pid or x['photo']
    c = fit(photo(pid), W, H, 0.5, yb).convert('RGBA')
    c = Image.alpha_composite(c, grad_cached((W, H), 470, 1350, 0, 245))
    c = Image.alpha_composite(c, grad_cached((W, H), 0, 220, 150, 0))
    d = ImageDraw.Draw(c)
    c.alpha_composite(logo(96), (60, 56))
    spaced(d, (176, 86), 'NOIDA FARMHOUSE PARTY', PS(24, 'SemiBold'), CREAM, 4)
    spaced(d, (176, 118), 'SECTOR 135 · NOIDA', PS(20, 'Medium'), CH, 4)
    y = 820
    spaced(d, (80, y), x['kicker'].upper(), PS(28, 'SemiBold'), CH, 5); y += 58
    f, L = fitwrap(d, x['head'], PF, 92, W - 160, 3, 56)
    for l in L: d.text((78, y), l, font=f, fill=CREAM); y += int(f.size * 1.16)
    y += 10; d.line((80, y, 200, y), fill=CH, width=3); y += 26
    if x.get('en'):
        f2, L2 = fitwrap(d, x['en'], PS, 34, W - 160, 2, 26)
        for l in L2: d.text((80, y), l, font=f2, fill=SOFT); y += int(f2.size * 1.45)
    if swipe:
        spaced(d, (W - 80 - 190, H - 80), 'SWIPE', PS(24, 'SemiBold'), CH, 4)
        ax = W - 80 - 70; ay = H - 64
        d.line((ax, ay, ax + 60, ay), fill=CH, width=3); d.polygon([(ax + 60, ay - 9), (ax + 72, ay), (ax + 60, ay + 9)], fill=CH)
    else:
        spaced(d, (80, H - 78), '+91 78277 13708', PS(24, 'SemiBold'), CH, 3)
    return c.convert('RGB')

def slide_setting(x, pid):
    c = Image.new('RGB', (W, H), CREAM)
    c.paste(fit(photo(pid), W, 780, 0.5, 0.55), (0, 0))
    d = ImageDraw.Draw(c)
    y = 840
    spaced(d, (80, y), 'THE SETTING', PS(26, 'SemiBold'), (150, 120, 60), 5); y += 56
    f, L = fitwrap(d, x['body'], PI, 44, W - 160, 6, 30)
    for l in L: d.text((80, y), l, font=f, fill=INK); y += int(f.size * 1.32)
    brandbar(c, H - 70, light=False)
    return c

def slide_points(x, pids):
    c = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(c)
    spaced(d, (80, 110), x['kicker'].upper(), PS(26, 'SemiBold'), (150, 120, 60), 5)
    d.text((78, 160), x['ptitle'], font=PF(76), fill=NIGHT)
    y = 330
    for i, p in enumerate(x['points'][:4]):
        d.ellipse((80, y, 156, y + 76), outline=CH, width=3)
        n = f'{i+1:02d}'; f = PF(34, 'Bold'); tw = d.textlength(n, font=f)
        d.text((118 - tw / 2, y + 14), n, font=f, fill=NIGHT)
        f2, L = fitwrap(d, p, PS, 38, W - 300, 2, 28)
        yy = y + (76 - len(L) * int(f2.size * 1.3)) // 2
        for l in L: d.text((190, yy), l, font=f2, fill=INK); yy += int(f2.size * 1.3)
        y += 128
    sw = (W - 160 - 40) // 3
    for i, pid in enumerate(pids[:3]):
        c.paste(fit(photo(pid), sw, 300), (80 + i * (sw + 20), 880))
    brandbar(c, H - 70, light=False)
    return c

def slide_point_big(x, i, pid):
    c = Image.new('RGB', (W, H), CREAM)
    c.paste(fit(photo(pid), W, 560, 0.5, 0.5), (0, H - 560))
    d = ImageDraw.Draw(c)
    spaced(d, (80, 100), x['kicker'].upper(), PS(26, 'SemiBold'), (150, 120, 60), 5)
    d.text((70, 140), f'{i+1:02d}', font=PF(200, 'Bold'), fill=CH)
    f, L = fitwrap(d, x['points'][i], PF, 78, W - 160, 3, 48)
    y = 420
    for l in L: d.text((78, y), l, font=f, fill=NIGHT); y += int(f.size * 1.2)
    spaced(d, (80, 740), f'{i+1} / 4', PS(24, 'Medium'), (120, 130, 124), 3)
    return c

def slide_know(x):
    c = Image.new('RGB', (W, H), NIGHT); d = ImageDraw.Draw(c)
    spaced(d, (80, 120), 'GOOD TO KNOW', PS(28, 'SemiBold'), CH, 6)
    d.text((78, 170), 'House notes', font=PF(84), fill=CREAM)
    items = ['Up to 150 guests on the lawn', 'One group at a time, fully private', 'Music till 10 pm as per local rules',
             'FL-11 one-day licence if liquor is served', 'Three bedrooms for a stay-over']
    y = 380
    for t in items:
        d.polygon([(92, y + 10), (102, y + 22), (92, y + 34), (82, y + 22)], fill=CH)
        d.text((136, y), t, font=PS(38), fill=SOFT); y += 118
    d.line((80, y + 10, 220, y + 10), fill=CH, width=3)
    brandbar(c, H - 80)
    return c

def slide_arrange(x, pid):
    c = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(c)
    c.paste(fit(photo(pid), W, 520, 0.5, 0.5), (0, 0))
    spaced(d, (80, 590), 'WE CAN ARRANGE', PS(26, 'SemiBold'), (150, 120, 60), 5)
    d.text((78, 636), 'One call, sorted', font=PF(72), fill=NIGHT)
    items = ['Catering partners', 'Décor and florals', 'DJ and sound till 10 pm', 'Rooms for the family']
    y = 780
    for t in items:
        d.text((80, y), '—', font=PS(36, 'Medium'), fill=CH); d.text((136, y), t, font=PS(38), fill=INK); y += 90
    brandbar(c, H - 70, light=False)
    return c

def slide_cta(x):
    c = Image.new('RGB', (W, H), DEEP); d = ImageDraw.Draw(c)
    c.paste(logo(220), (W // 2 - 110, 170), logo(220))
    t = 'Tell us your date'; f = PF(88); d.text((W / 2 - d.textlength(t, font=f) / 2, 450), t, font=f, fill=CREAM)
    t = 'and the guest count, we will send a quote'; f = PI(40); d.text((W / 2 - d.textlength(t, font=f) / 2, 570), t, font=f, fill=CH)
    d.line((W / 2 - 80, 670, W / 2 + 80, 670), fill=CH, width=3)
    t = '+91 78277 13708'; f = PS(64, 'SemiBold'); d.text((W / 2 - d.textlength(t, font=f) / 2, 720), t, font=f, fill=CREAM)
    t = 'Call / WhatsApp  ·  or DM “DATE”'; f = PS(32); d.text((W / 2 - d.textlength(t, font=f) / 2, 815), t, font=f, fill=SOFT)
    t = 'noidafarmhouseparty.com'; f = PS(34, 'Medium'); d.text((W / 2 - d.textlength(t, font=f) / 2, 900), t, font=f, fill=CH)
    brandbar(c, H - 110)
    return c

def carousel(x):
    p = x['photo']; alt = [(p + k - 1) % 8 + 1 for k in (1, 3, 5, 2, 6)]
    S = [cover(x, swipe=True)]
    if x['guide']:
        S += [slide_point_big(x, i, alt[i]) for i in range(4)]
    else:
        S += [slide_setting(x, alt[0]), slide_points(x, alt[1:4]), slide_know(x), slide_arrange(x, alt[4])]
    S.append(slide_cta(x))
    return S

# ---------- video overlays (1080x1920 RGBA) ----------
VW, VH = 1080, 1920

def ov_title(x, top=210):
    c = Image.new('RGBA', (VW, VH), (0, 0, 0, 0))
    c.alpha_composite(grad_cached((VW, VH), 0, 980, 205, 0)); d = ImageDraw.Draw(c)
    c.alpha_composite(logo(84), (VW // 2 - 42, top - 120))
    spaced(d, (VW / 2, top), x['kicker'].upper(), PS(32, 'SemiBold'), CH, 6, 'm')
    f, L = fitwrap(d, x['head'], PF, 100, VW - 140, 3, 60)
    y = top + 64
    for l in L:
        tw = d.textlength(l, font=f)
        d.text((VW / 2 - tw / 2 + 3, y + 4), l, font=f, fill=(0, 0, 0, 110))
        d.text((VW / 2 - tw / 2, y), l, font=f, fill=CREAM); y += int(f.size * 1.15)
    if x.get('en'):
        f2, L2 = fitwrap(d, x['en'], PS, 38, VW - 180, 2, 28); y += 14
        for l in L2:
            tw = d.textlength(l, font=f2); d.text((VW / 2 - tw / 2, y), l, font=f2, fill=SOFT); y += int(f2.size * 1.45)
    return c

def ov_label(text, n, y=1500):
    c = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    f, L = fitwrap(d, text, PF, 64, VW - 260, 2, 44)
    h = 90 + len(L) * int(f.size * 1.2)
    d.rounded_rectangle((80, y, VW - 80, y + h), radius=26, fill=DEEP + (215,), outline=CH + (255,), width=2)
    d.text((120, y + 26), f'{n:02d}', font=PS(28, 'SemiBold'), fill=CH)
    yy = y + 62
    for l in L: d.text((120, yy), l, font=f, fill=CREAM); yy += int(f.size * 1.2)
    return c

def ov_card_head(x):
    c = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((70, 300, VW - 70, 1480), radius=36, fill=CREAM + (244,))
    spaced(d, (VW / 2, 370), x['kicker'].upper(), PS(30, 'SemiBold'), (150, 120, 60), 6, 'm')
    f, L = fitwrap(d, x['en'] or x['head'], PF, 74, VW - 260, 3, 48); y = 430
    for l in L:
        tw = d.textlength(l, font=f); d.text((VW / 2 - tw / 2, y), l, font=f, fill=NIGHT); y += int(f.size * 1.18)
    d.line((VW / 2 - 70, y + 20, VW / 2 + 70, y + 20), fill=CH, width=3)
    return c, y + 70

def ov_card_point(i, text, y0):
    c = Image.new('RGBA', (VW, VH), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    y = y0 + i * 190
    d.ellipse((130, y, 210, y + 80), outline=CH + (255,), width=3)
    n = f'{i+1:02d}'; f = PF(36, 'Bold'); tw = d.textlength(n, font=f); d.text((170 - tw / 2, y + 14), n, font=f, fill=NIGHT)
    f2, L = fitwrap(d, text, PS, 42, VW - 400, 2, 30)
    yy = y + (80 - len(L) * int(f2.size * 1.3)) // 2
    for l in L: d.text((240, yy), l, font=f2, fill=INK); yy += int(f2.size * 1.3)
    return c

def ov_end():
    c = Image.new('RGBA', (VW, VH), DEEP + (255,)); d = ImageDraw.Draw(c)
    c.alpha_composite(logo(260), (VW // 2 - 130, 520))
    for t, f, col, y in [('Noida Farmhouse Party', PF(84), CREAM, 860), ('Private pool farmhouse · Sector 135, Noida', PI(40), CH, 975),
                         ('+91 78277 13708', PS(70, 'SemiBold'), CREAM, 1120), ('Call / WhatsApp for a quote', PS(36), SOFT, 1220),
                         ('noidafarmhouseparty.com', PS(38, 'Medium'), CH, 1300)]:
        d.text((VW / 2 - d.textlength(t, font=f) / 2, y), t, font=f, fill=col)
    d.line((VW / 2 - 90, 1090, VW / 2 + 90, 1090), fill=CH, width=3)
    return c

def ov_caption(text, y=1430):
    c = Image.new('RGBA', (VW, VH), (0, 0, 0, 0))
    c.alpha_composite(grad_cached((VW, VH), 1180, 1920, 0, 225)); d = ImageDraw.Draw(c)
    f, L = fitwrap(d, text, PI, 50, VW - 200, 3, 34); yy = y
    for l in L:
        tw = d.textlength(l, font=f); d.text((VW / 2 - tw / 2, yy), l, font=f, fill=CREAM); yy += int(f.size * 1.3)
    return c

SPACE = {1: 'A lawn for up to 150 guests', 2: 'A private pool by the house', 3: "A shallow kids' section", 4: 'Palms around the pool deck',
         5: 'A shaded porch with steps to the lawn', 6: 'The lawn, seen from the terrace', 7: 'An open terrace above the lawn', 8: 'A pool deck for sundowners'}
