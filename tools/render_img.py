import os
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
O = os.path.join(ROOT,'media','img'); os.makedirs(O, exist_ok=True)
days = json.load(open(os.path.join(ROOT,'content','plan.json')))
n = 0
for x in days:
    if x['fmt'] == 'carousel':
        for i, s in enumerate(carousel(x)):
            s.save(f"{O}/{x['id']}_{i+1}.jpg", quality=90); n += 1
    elif x['fmt'] == 'single':
        cover(x, yb=0.5).save(f"{O}/{x['id']}_1.jpg", quality=92); n += 1
print(n)
