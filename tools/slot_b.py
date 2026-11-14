"""Second daily Instagram/Facebook slot (12:30 IST): reel days get a carousel, post days get the day's reel."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gfx import carousel
from plan import Q
PJ = os.path.join(ROOT, 'content', 'plan.json')
SITE = 'https://noidafarmhouseparty.com'; PHONE = '+91 78277 13708'
TAGS2 = ['#noidaparties', '#weekendplans', '#partyplanning', '#venueinnoida', '#greaternoida']
def tags(x):
    return ' '.join(['#farmhouseinnoida', '#' + x['tag'], TAGS2[x['qi'] % 5], '#noidafarmhouse', '#delhincr'])
def block(x):
    return ['', "✦ Private pool with kids' section · Lawn for up to 150 · 3 bedrooms",
            '📍 Sector 135, Noida · beside the Noida–Greater Noida Expressway', '🌐 noidafarmhouseparty.com',
            f'📞 Call / WhatsApp {PHONE} · or DM “DATE” for a quote', '', tags(x)]
def build(days):
    for x in days:
        if x['fmt'] == 'reel':
            x['b_fmt'] = 'carousel'
            pts = '\n'.join(f'{k+1:02d} · {p}' for k, p in enumerate(x['points'][:4]))
            L = [f"{x['kw']} — {x['ptitle']} ✨", '', f"{x['head'].rstrip('.')}{'' if x['head'][-1:] in '!?' else '.'} Save this for your planning list ➝", '', pts] + block(x)
        else:
            x['b_fmt'] = 'reel'
            q = Q.get(x['typ'], Q['day'])[(x['qi'] + 2) % len(Q.get(x['typ'], Q['day']))]
            L = [f"{x['kw']} | {x['en'] or x['head']} 🎬", '', f"{x['head'].rstrip('.')}{'' if x['head'][-1:] in '!?' else '.'}", '', f"👇 {q}"] + block(x)
        x['b_ig'] = '\n'.join(L)
        x['b_fb'] = x['b_ig'].replace('🌐 noidafarmhouseparty.com', f"👉 {SITE}{x['path']}?utm_source=facebook&utm_medium=social&utm_campaign={x['id']}b")
    return days
if __name__ == '__main__':
    days = build(json.load(open(PJ)))
    json.dump(days, open(PJ, 'w'), ensure_ascii=False, indent=1)
    n = 0
    if '--render' in sys.argv:
        for x in days:
            if x['b_fmt'] != 'carousel': continue
            y = dict(x); y['photo'] = (x['photo'] + 2) % 8 + 1
            for k, s in enumerate(carousel(y)):
                s.save(os.path.join(ROOT, 'media', 'img', f"{x['id']}_b{k+1}.jpg"), quality=88); n += 1
    from collections import Counter
    print(Counter(x['b_fmt'] for x in days), n)
