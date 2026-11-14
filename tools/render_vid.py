import os
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
OUT = os.path.join(ROOT,'media','video'); TMP = '/tmp/nfpv'
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
END = None

def save(im, name):
    p = f'{TMP}/{name}.png'; im.save(p, optimize=False, compress_level=1); return p

def alts(x):
    p = x['photo']; return [p] + [(p + k - 1) % 8 + 1 for k in (2, 4, 6, 1, 3)]

def pan_expr(dirn, D):
    return f"(iw-ow)*(t/{D})" if dirn == 0 else f"(iw-ow)*(1-t/{D})"

def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-1500:])

ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-maxrate', '2600k', '-bufsize', '5200k', '-pix_fmt', 'yuv420p',
       '-r', '30', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-shortest']

def render(x):
    global END
    if END is None: END = save(ov_end(), 'end')
    uid = x['id']; vt = x['vt']; out = f"{OUT}/{uid}.mp4"
    if os.path.exists(out): return out
    A = alts(x); aud = os.path.join(ROOT,"tools","audio",f"a{x['qi'] % 6}.wav"); dirn = x['qi'] % 2
    if vt in ('hook', 'tour'):
        D = 9.5
        tt = save(ov_title(x, top=210 if vt == 'hook' else 170), uid + 't')
        extra_in = []; extra_f = ''
        if vt == 'tour':
            cap = save(ov_caption(x['body'][:150] if len(x['body']) < 150 else x['en'] or x['head']), uid + 'c')
            extra_in = ['-loop', '1', '-framerate', '30', '-t', str(D), '-i', cap]
        pid = A[0] if vt == 'hook' else A[1]
        inp = ['-loop', '1', '-framerate', '30', '-t', str(D), '-i', P % pid,
               '-loop', '1', '-framerate', '30', '-t', str(D), '-i', tt,
               '-loop', '1', '-framerate', '30', '-t', str(D), '-i', END] + extra_in + ['-i', aud]
        ai = 4 if vt == 'tour' else 3
        f = (f"[0]scale=-2:1920,crop=1080:1920:x='{pan_expr(dirn, D)}':y=0,setsar=1,format=rgba[b];"
             f"[1]format=rgba,fade=out:st=7.3:d=0.4:alpha=1[t];"
             f"[2]format=rgba,fade=in:st=7.7:d=0.5:alpha=1[e];[b][t]overlay[v1];")
        if vt == 'tour':
            f += f"[3]format=rgba,fade=in:st=1.4:d=0.8:alpha=1,fade=out:st=7.3:d=0.4:alpha=1[c];[v1][c]overlay[v2];[v2][e]overlay,format=yuv420p[v]"
        else:
            f += "[v1][e]overlay,format=yuv420p[v]"
        f += f";[{ai}]atrim=0:{D},afade=out:st={D-1.2}:d=1.2[a]"
        run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', f, '-map', '[v]', '-map', '[a]', '-t', str(D)] + ENC + [out])
    elif vt == 'trio':
        segs = [3.0, 3.0, 4.3]; X = 0.35; D = sum(segs) - 2 * X
        tt = save(ov_title(x, top=200), uid + 't')
        labs = [save(ov_label(SPACE[A[i]], i + 1), f'{uid}l{i}') for i in range(3)]
        inp = []
        for i in range(3): inp += ['-loop', '1', '-framerate', '30', '-t', str(segs[i]), '-i', P % A[i]]
        for p in [tt] + labs + [END]: inp += ['-loop', '1', '-framerate', '30', '-t', str(D), '-i', p]
        inp += ['-i', aud]
        f = ''
        for i in range(3):
            f += f"[{i}]scale=-2:1920,crop=1080:1920:x='{pan_expr((dirn + i) % 2, segs[i])}':y=0,setsar=1,fps=30,format=yuv420p[s{i}];"
        o1 = segs[0] - X; o2 = segs[0] + segs[1] - 2 * X
        f += f"[s0][s1]xfade=transition=fade:duration={X}:offset={o1}[x1];[x1][s2]xfade=transition=fade:duration={X}:offset={o2},format=rgba[b];"
        f += "[3]format=rgba,fade=out:st=7.6:d=0.4:alpha=1[t];"
        st = [0.5, o1 + 0.4, o2 + 0.4]; en = [o1 - 0.1, o2 - 0.1, 7.6]
        for i in range(3):
            f += f"[{4+i}]format=rgba,fade=in:st={st[i]:.2f}:d=0.4:alpha=1,fade=out:st={en[i]:.2f}:d=0.35:alpha=1[l{i}];"
        f += "[7]format=rgba,fade=in:st=8.0:d=0.5:alpha=1[e];[b][t]overlay[v1];[v1][l0]overlay[v2];[v2][l1]overlay[v3];[v3][l2]overlay[v4];[v4][e]overlay,format=yuv420p[v];"
        f += f"[8]atrim=0:{D},afade=out:st={D-1.2}:d=1.2[a]"
        run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', f, '-map', '[v]', '-map', '[a]', '-t', f'{D:.2f}'] + ENC + [out])
    else:  # guide
        D = 10.5
        bgp = f'{TMP}/{uid}bg.jpg'
        fit(photo(A[0]), 1240, 2204).filter(ImageFilter.GaussianBlur(16)).save(bgp, quality=88)
        head, y0 = ov_card_head(x); hp = save(head, uid + 'h')
        pts = [save(ov_card_point(i, p, y0), f'{uid}p{i}') for i, p in enumerate(x['points'][:4])]
        inp = ['-loop', '1', '-framerate', '30', '-t', str(D), '-i', bgp]
        for p in [hp] + pts + [END]: inp += ['-loop', '1', '-framerate', '30', '-t', str(D), '-i', p]
        inp += ['-i', aud]
        f = f"[0]crop=1080:1920:x='160*t/{D}':y='284*t/{D}',setsar=1,format=rgba[b];"
        f += "[1]format=rgba,fade=out:st=8.0:d=0.4:alpha=1[h];"
        for i in range(4):
            f += f"[{2+i}]format=rgba,fade=in:st={1.2+i*1.15:.2f}:d=0.4:alpha=1,fade=out:st=8.0:d=0.4:alpha=1[p{i}];"
        f += "[6]format=rgba,fade=in:st=8.3:d=0.5:alpha=1[e];[b][h]overlay[v0];[v0][p0]overlay[v1];[v1][p1]overlay[v2];[v2][p2]overlay[v3];[v3][p3]overlay[v4];[v4][e]overlay,format=yuv420p[v];"
        f += f"[7]atrim=0:{D},afade=out:st={D-1.2}:d=1.2[a]"
        run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', f, '-map', '[v]', '-map', '[a]', '-t', str(D)] + ENC + [out])
    for fn in os.listdir(TMP):
        if fn.startswith(uid): os.remove(f'{TMP}/{fn}')
    return out

if __name__ == '__main__':
    days = json.load(open(os.path.join(ROOT,'content','plan.json')))
    sel = sys.argv[1:]
    todo = [x for x in days if not sel or x['id'] in sel]
    for x in todo:
        try:
            p = render(x); print(x['id'], x['vt'], os.path.getsize(p) // 1024, 'KB', flush=True)
        except Exception as e:
            print('ERR', x['id'], x['vt'], str(e)[-600:], flush=True)
