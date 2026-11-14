#!/usr/bin/env python3
"""Noida Farmhouse Party — daily auto-publisher (GitHub Actions).

Tasks: story (09:30 IST), meta_b (12:30, 2nd IG+FB post), threads (13:00), youtube (18:00), meta (19:30 = Instagram + Facebook).
Publishes only TODAY's item (IST) from content/plan.json. Never back-fills, never boosts, never pays.
Media is served from GitHub Pages: https://<owner>.github.io/<repo>/media/...
"""
import argparse, datetime as dt, json, os, subprocess, sys, time, hashlib
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = {x['date']: x for x in json.load(open(os.path.join(ROOT, 'content', 'plan.json')))}
STATE = os.path.join(ROOT, 'state', 'posted.json')
CUTOFF = json.load(open(os.path.join(ROOT, 'state', 'cutoff.json')))
G = 'https://graph.facebook.com/v23.0'
TH = 'https://graph.threads.net/v1.0'
SITE = 'https://noidafarmhouseparty.com'
MEDIA = os.environ.get('NFP_MEDIA_BASE') or 'https://{}.github.io/{}/media'.format(*os.environ.get('GITHUB_REPOSITORY', 'noidafarmhouseparty-jpg/nfp-social').split('/'))
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
DRY = False

def log(*a): print('[nfp]', *a, flush=True)

def load_state():
    try: return json.load(open(STATE))
    except Exception: return {}

def save_state(s):
    json.dump(s, open(STATE, 'w'), indent=1, sort_keys=True)

def req(method, url, **kw):
    if DRY:
        log('DRY', method, url.split('?')[0], {k: (str(v)[:60] + '…') for k, v in (kw.get('data') or kw.get('params') or {}).items() if 'token' not in k})
        return {'id': 'dry'}
    for attempt in range(3):
        r = requests.request(method, url, timeout=120, **kw)
        if r.status_code < 500: break
        time.sleep(10 * (attempt + 1))
    try: j = r.json()
    except Exception: j = {'raw': r.text[:300]}
    if r.status_code >= 400 or (isinstance(j, dict) and 'error' in j):
        raise RuntimeError(f'{method} {url.split("?")[0]} -> {r.status_code} {json.dumps(j)[:500]}')
    return j

def need(*names):
    miss = [n for n in names if not os.environ.get(n)]
    if miss:
        log('SKIP: secrets not set yet:', ', '.join(miss)); sys.exit(0)

def ig_caption(x):
    return x['ig'].replace('📞 Call', '🌐 noidafarmhouseparty.com\n📞 Call')

# ---------------- Meta (Facebook Page + Instagram) ----------------
def meta_ids(tok):
    page = os.environ.get('FB_PAGE_ID') or req('GET', f'{G}/me', params={'fields': 'id,name', 'access_token': tok})['id']
    ig = os.environ.get('IG_USER_ID') or req('GET', f'{G}/{page}', params={'fields': 'instagram_business_account', 'access_token': tok}).get('instagram_business_account', {}).get('id')
    if not ig and not DRY: raise RuntimeError('Instagram business account not linked to the Page token')
    return page, ig or 'dry-ig'

def ig_wait(cid, tok, limit=600):
    if DRY: return
    t0 = time.time()
    while time.time() - t0 < limit:
        s = req('GET', f'{G}/{cid}', params={'fields': 'status_code,status', 'access_token': tok})
        if s.get('status_code') == 'FINISHED': return
        if s.get('status_code') in ('ERROR', 'EXPIRED'): raise RuntimeError(f'IG container {cid}: {s}')
        time.sleep(10)
    raise RuntimeError(f'IG container {cid} not ready after {limit}s')

def ig_publish(ig, cid, tok):
    ig_wait(cid, tok)
    return req('POST', f'{G}/{ig}/media_publish', data={'creation_id': cid, 'access_token': tok})['id']

def task_meta(x, st, slot=''):
    need('META_PAGE_TOKEN'); tok = os.environ['META_PAGE_TOKEN']; page, ig = meta_ids(tok)
    i = x['id']; done = []
    if slot == 'b': cap, fbcap, fmt, sfx = x['b_ig'], x['b_fb'], x['b_fmt'], 'b'
    else: cap, fbcap, fmt, sfx = ig_caption(x), x['fb'], x['fmt'], ''
    K = lambda p: f'{p}{sfx}:{x["date"]}'
    if fmt == 'reel':
        url = f'{MEDIA}/video/{i}.mp4'
        if not st.get(K('ig')):
            c = req('POST', f'{G}/{ig}/media', data={'media_type': 'REELS', 'video_url': url, 'caption': cap, 'share_to_feed': 'true', 'thumb_offset': '0', 'access_token': tok})['id']
            st[K('ig')] = ig_publish(ig, c, tok); done.append('ig-reel')
        if not st.get(K('fb')):
            s = req('POST', f'{G}/{page}/video_reels', data={'upload_phase': 'start', 'access_token': tok})
            if not DRY:
                r = requests.post(s['upload_url'], headers={'Authorization': f'OAuth {tok}', 'file_url': url}, timeout=300)
                if r.status_code >= 400: raise RuntimeError(f'FB reel upload {r.status_code} {r.text[:300]}')
            req('POST', f'{G}/{page}/video_reels', data={'upload_phase': 'finish', 'video_id': s.get('video_id', 'dry'), 'video_state': 'PUBLISHED', 'description': fbcap, 'access_token': tok})
            st[K('fb')] = s.get('video_id', 'dry'); done.append('fb-reel')
    else:
        n = 6 if fmt == 'carousel' else 1
        urls = [f'{MEDIA}/img/{i}_{sfx}{k}.jpg' for k in range(1, n + 1)]
        if not st.get(K('ig')):
            if n == 1:
                c = req('POST', f'{G}/{ig}/media', data={'image_url': urls[0], 'caption': cap, 'alt_text': x['alt'], 'access_token': tok})['id']
            else:
                kids = [req('POST', f'{G}/{ig}/media', data={'image_url': u, 'is_carousel_item': 'true', 'alt_text': x['alt'], 'access_token': tok})['id'] for u in urls]
                for k in kids: ig_wait(k, tok)
                c = req('POST', f'{G}/{ig}/media', data={'media_type': 'CAROUSEL', 'children': ','.join(kids), 'caption': cap, 'access_token': tok})['id']
            st[K('ig')] = ig_publish(ig, c, tok); done.append('ig-' + fmt + sfx)
        if not st.get(K('fb')):
            if n == 1:
                r = req('POST', f'{G}/{page}/photos', data={'url': urls[0], 'message': fbcap, 'access_token': tok})
            else:
                ids = [req('POST', f'{G}/{page}/photos', data={'url': u, 'published': 'false', 'access_token': tok})['id'] for u in urls]
                data = {'message': fbcap, 'access_token': tok}
                for k, pid in enumerate(ids): data[f'attached_media[{k}]'] = json.dumps({'media_fbid': pid})
                r = req('POST', f'{G}/{page}/feed', data=data)
            st[K('fb')] = r.get('id') or r.get('post_id'); done.append('fb-' + fmt + sfx)
    return done

def task_story(x, st):
    need('META_PAGE_TOKEN'); tok = os.environ['META_PAGE_TOKEN']; page, ig = meta_ids(tok)
    url = f'{MEDIA}/story/{x["id"]}.jpg'; done = []
    if not st.get(f'igstory:{x["date"]}'):
        c = req('POST', f'{G}/{ig}/media', data={'media_type': 'STORIES', 'image_url': url, 'access_token': tok})['id']
        st[f'igstory:{x["date"]}'] = ig_publish(ig, c, tok); done.append('ig-story')
    if not st.get(f'fbstory:{x["date"]}'):
        pid = req('POST', f'{G}/{page}/photos', data={'url': url, 'published': 'false', 'access_token': tok})['id']
        st[f'fbstory:{x["date"]}'] = req('POST', f'{G}/{page}/photo_stories', data={'photo_id': pid, 'access_token': tok}).get('post_id', pid); done.append('fb-story')
    return done

# ---------------- Threads ----------------
def threads_token():
    tok = os.environ.get('THREADS_TOKEN'); key = os.environ.get('YT_CLIENT_SECRET') or os.environ.get('META_PAGE_TOKEN', '')
    enc = os.path.join(ROOT, 'state', 'threads_token.enc')
    if os.path.exists(enc) and key:
        try:
            tok = subprocess.run(['openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-a', '-A', '-in', enc, '-pass', 'env:NFPK'], env={**os.environ, 'NFPK': hashlib.sha256(key.encode()).hexdigest()}, capture_output=True, text=True, check=True).stdout.strip() or tok
        except Exception as e: log('threads token decrypt failed, using secret', e)
    return tok, key, enc

def threads_refresh(st):
    tok, key, enc = threads_token()
    if DRY or not tok or not key: return
    last = st.get('threads_refreshed', '2000-01-01')
    if (dt.date.today() - dt.date.fromisoformat(last)).days < 7: return
    try:
        new = req('GET', 'https://graph.threads.net/refresh_access_token', params={'grant_type': 'th_refresh_token', 'access_token': tok})['access_token']
        subprocess.run(['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-a', '-A', '-salt', '-out', enc, '-pass', 'env:NFPK'], input=new, env={**os.environ, 'NFPK': hashlib.sha256(key.encode()).hexdigest()}, text=True, check=True)
        st['threads_refreshed'] = dt.date.today().isoformat(); log('threads token refreshed')
    except Exception as e: log('threads refresh failed (will retry next run):', e)

def task_threads(x, st):
    need('THREADS_TOKEN'); tok = threads_token()[0]
    if st.get(f'threads:{x["date"]}'): return []
    uid = os.environ.get('THREADS_USER_ID') or req('GET', f'{TH}/me', params={'fields': 'id', 'access_token': tok})['id']
    c = req('POST', f'{TH}/{uid}/threads', data={'media_type': 'TEXT', 'text': x['threads'], 'access_token': tok})['id']
    if not DRY: time.sleep(30)
    st[f'threads:{x["date"]}'] = req('POST', f'{TH}/{uid}/threads_publish', data={'creation_id': c, 'access_token': tok})['id']
    threads_refresh(st)
    return ['threads']

# ---------------- YouTube ----------------
def task_youtube(x, st):
    need('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN')
    if st.get(f'yt:{x["date"]}'): return []
    if DRY: log('DRY youtube upload', x['yt_title']); return ['youtube']
    at = requests.post('https://oauth2.googleapis.com/token', data={'client_id': os.environ['YT_CLIENT_ID'], 'client_secret': os.environ['YT_CLIENT_SECRET'], 'refresh_token': os.environ['YT_REFRESH_TOKEN'], 'grant_type': 'refresh_token'}, timeout=60).json()
    if 'access_token' not in at: raise RuntimeError(f'YouTube token refresh failed: {at}')
    H = {'Authorization': 'Bearer ' + at['access_token']}
    vid = requests.get(f'{MEDIA}/video/{x["id"]}.mp4', timeout=300); vid.raise_for_status()
    meta = {'snippet': {'title': x['yt_title'][:100], 'description': x['yt_desc'], 'tags': x['yt_tags'], 'categoryId': '19', 'defaultLanguage': 'en'},
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'embeddable': True}}
    r = requests.post('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status', headers={**H, 'Content-Type': 'application/json', 'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(len(vid.content))}, data=json.dumps(meta), timeout=60)
    if r.status_code >= 400: raise RuntimeError(f'YT init {r.status_code} {r.text[:300]}')
    up = requests.put(r.headers['Location'], headers={**H, 'Content-Type': 'video/mp4'}, data=vid.content, timeout=600)
    if up.status_code >= 400: raise RuntimeError(f'YT upload {up.status_code} {up.text[:300]}')
    vid_id = up.json()['id']; st[f'yt:{x["date"]}'] = vid_id
    try:
        th = requests.get(f'{MEDIA}/thumb/{x["id"]}.jpg', timeout=60).content
        t = requests.post(f'https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={vid_id}&uploadType=media', headers={**H, 'Content-Type': 'image/jpeg'}, data=th, timeout=60)
        log('thumbnail', t.status_code)
    except Exception as e: log('thumbnail skipped', e)
    return ['youtube ' + vid_id]

TASKS = {'meta': task_meta, 'meta_b': lambda x, st: task_meta(x, st, 'b'), 'story': task_story, 'threads': task_threads, 'youtube': task_youtube}
CUT = {'meta': 'meta', 'meta_b': 'meta_b', 'story': 'story', 'threads': 'threads', 'youtube': 'youtube'}

def main():
    global DRY
    ap = argparse.ArgumentParser(); ap.add_argument('task', choices=list(TASKS) + ['check']); ap.add_argument('--date'); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args(); DRY = a.dry or os.environ.get('NFP_DRY') == '1'
    if a.task == 'check': return check()
    day = a.date or dt.datetime.now(IST).date().isoformat()
    x = PLAN.get(day)
    if not x: log('no plan entry for', day); return
    if day <= CUTOFF.get(CUT[a.task], '0000'): log(f'{a.task}: {day} already scheduled natively (cutoff {CUTOFF[CUT[a.task]]}); skip'); return
    st = load_state()
    try:
        done = TASKS[a.task](x, st)
        log(a.task, day, x['fmt'], '->', done or 'already posted')
    finally:
        if not DRY: save_state(st)

def check():
    ok = True
    if os.environ.get('META_PAGE_TOKEN'):
        try:
            tok = os.environ['META_PAGE_TOKEN']; page, ig = meta_ids(tok)
            name = req('GET', f'{G}/{page}', params={'fields': 'name', 'access_token': tok}).get('name')
            iu = req('GET', f'{G}/{ig}', params={'fields': 'username', 'access_token': tok}).get('username')
            log('META OK  page:', name, page, '| instagram:', iu, ig)
        except Exception as e: ok = False; log('META FAIL', e)
    else: log('META_PAGE_TOKEN not set')
    if os.environ.get('THREADS_TOKEN'):
        try: log('THREADS OK', req('GET', f'{TH}/me', params={'fields': 'id,username', 'access_token': threads_token()[0]}))
        except Exception as e: ok = False; log('THREADS FAIL', e)
    else: log('THREADS_TOKEN not set')
    if os.environ.get('YT_REFRESH_TOKEN'):
        at = requests.post('https://oauth2.googleapis.com/token', data={'client_id': os.environ.get('YT_CLIENT_ID'), 'client_secret': os.environ.get('YT_CLIENT_SECRET'), 'refresh_token': os.environ['YT_REFRESH_TOKEN'], 'grant_type': 'refresh_token'}, timeout=60).json()
        if 'access_token' in at:
            ch = requests.get('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true', headers={'Authorization': 'Bearer ' + at['access_token']}, timeout=60).json()
            log('YOUTUBE OK', [c['snippet']['title'] for c in ch.get('items', [])])
        else: ok = False; log('YOUTUBE FAIL', at)
    else: log('YT_REFRESH_TOKEN not set')
    r = requests.head(f'{MEDIA}/video/n20261115.mp4', timeout=30); log('MEDIA', r.status_code, r.headers.get('content-type'), MEDIA)
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
