import os
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, datetime as dt, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import B, G

SITE = 'https://noidafarmhouseparty.com'
PHONE = '+91 78277 13708'
cal = json.load(open(os.path.join(ROOT,'content','gbp_cal.json')))
extra = json.load(open(os.path.join(ROOT,'content','gbp_extra.json')))

EXTRA_BODY = {
 'e20261117': ("Winter nights on a private lawn", "A crackling bonfire on the lawn, chai and corn on the porch, and the stars doing the rest. Music till 10 pm, three bedrooms if you stay over.", '/bonfire-party-in-noida/'),
 'e20261120': ("Lawn, pool and rooms for your birthday", "Cake on the porch, games on the lawn, a pool for the brave and rooms if the party runs late.", '/birthday-party-farmhouse-noida/'),
 'e20261123': ("A private New Year's Eve in Noida", "Ring in 2027 on your own lawn with your own people. Music till 10 pm as per local rules, then a cosy countdown indoors.", '/new-year-party-farmhouse-noida/'),
 'e20261126': ("Rituals on the porch, lunch on the lawn", "Keep the roka close and beautiful: family on the porch, a long lunch on the lawn and portraits by the pool.", '/roka-ceremony-venue-in-noida/'),
 'e20261129': ("Team days beside the Expressway", "Workshop on the porch, cricket on the lawn, lunch under the sky. Projector and catering can be arranged.", '/team-outing-places-in-noida/'),
 'e20261202': ("Lawn, pool deck and winter sun", "This month's kitty on a sunny lawn: games, a long lunch and photos by the pool.", '/kitty-party-places-in-noida/'),
 'e20261205': ("Private pool, 3 bedrooms, lawn", "Skip the hotel room. Book the whole farmhouse with its own pool for your group.", '/villa-with-private-pool-in-noida/'),
 'e20261208': ("Pool, palms and a red-roof cottage", "Turquoise water, tall palms and a cottage that looks great in every frame.", '/pre-wedding-shoot-location-in-noida/'),
 'e20261211': ("Lawn for 150, lights and a dance floor", "Both families, one stage, one lawn. Music till 10 pm, rooms for the bride's side.", '/sangeet-venue-in-noida/'),
}

def typ_of(path, kicker=''):
    p = path + ' ' + kicker.lower()
    if 'licence' in p or 'noise-rules' in p: return 'guide'
    if any(k in p for k in ['wedding','roka','tilak','engagement','haldi','mehendi','naming','baby-shower','chowki','reception','marriage','sangeet']):
        return 'evening' if 'sangeet' in p or 'reception' in p else 'ceremony'
    if any(k in p for k in ['shoot','photoshoot']): return 'shoot'
    if any(k in p for k in ['night-stay','farm-stay','staycation','romantic-getaway','resort']): return 'stay'
    if any(k in p for k in ['cocktail','new-year','bonfire','candlelight','anniversary','farewell','movie','bachelor','christmas','proposal','lohri','retirement','launch']):
        return 'evening'
    if any(k in p for k in ['sector-135','near-delhi','ghaziabad','greater-noida','luxury','5-star','farmhouse-on-rent','villa','banquet','farmhouse-near-noida']) and 'birthday' not in p:
        return 'tour'
    return 'day'

KW_FIX = {
 '/': 'Private Pool Farmhouse in Noida',
 '/occasions-we-host/': 'Party & Event Venue in Noida',
 '/farmhouse-sector-135-noida/': 'Farmhouse in Sector 135, Noida',
 '/pre-wedding-haldi-mehendi-farmhouse-noida/': 'Haldi & Mehendi Venue in Noida',
 '/dj-noise-rules-noida/': 'DJ & Music Rules in Noida',
 '/farmhouse-party-liquor-licence-noida/': 'FL-11 Liquor Licence for Parties in Noida',
 '/wedding-venues-in-delhi-ncr/': 'Wedding Venues in Delhi NCR',
 '/5-star-hotel-alternative-in-noida/': '5-Star Hotel Alternative in Noida',
 '/kids-birthday-party-venue-noida/': "Kids' Birthday Party Venue in Noida",
 '/family-get-together-venue-noida/': 'Family Get-Together Venue in Noida',
 '/day-outing-near-noida/': 'Day Outing near Noida',
 '/farm-stay-in-noida/': 'Farm Stay in Noida',
 '/mata-ki-chowki-jagran-venue-noida/': 'Mata ki Chowki Venue in Noida',
}
SMALL = {'in','for','with','near','of','and','to','on'}
def kw(path):
    if path in KW_FIX: return KW_FIX[path]
    w = path.strip('/').split('-')
    if w[-1] == 'noida' and (len(w) < 2 or w[-2] not in ('in','near','greater')): w.insert(-1, 'in')
    out = []
    for i, x in enumerate(w):
        if x in SMALL and i: out.append(x)
        elif x in ('dj','ncr'): out.append(x.upper())
        else: out.append(x.capitalize())
    return ' '.join(out).replace('Farm Stay','Farm Stay')

def tag_of(path, typ):
    p = path
    for k, t in [('kids','kidsbirthdayparty'),('birthday','birthdayparty'),('haldi','haldiceremony'),('holi','holiparty'),
                 ('pool','poolparty'),('swimming','poolparty'),('corporate','corporateevents'),('team','teamouting'),
                 ('engagement','engagementceremony'),('roka','rokaceremony'),('sangeet','sangeetnight'),('wedding','intimatewedding'),
                 ('marriage','weddingvenue'),('shoot','prewedding'),('photoshoot','photoshootlocation'),('baby','babyshower'),
                 ('kitty','kittyparty'),('anniversary','anniversarycelebration'),('cocktail','cocktailparty'),('new-year','newyearparty'),
                 ('christmas','christmasparty'),('lohri','lohri'),('bonfire','bonfirenight'),('stay','staycation'),('family','familytime'),
                 ('reunion','reunion'),('farewell','farewellparty'),('bachelor','bachelorparty'),('bridal','bridalshower'),('chowki','matakichowki'),('naming','naamkaran'),('tilak','tilakceremony'),('retirement','retirementparty'),('proposal','proposal'),('candlelight','candlelightdinner'),('launch','productlaunch'),('workshop','workshop'),('yoga','wellnessretreat'),('film','shootlocation'),('movie','movienight'),('festival','festivevibes'),('banquet','partyvenue'),('rent','farmhouseonrent'),('resort','staycation'),('5-star','privatepool'),('day-outing','weekendgetaway'),('luxury','luxuryfarmhouse'),('villa','privatepool'),('sector-135','sector135noida'),('booking','farmhousebooking'),('licence','partyplanning'),('noise','partyplanning'),('occasions','partyvenue')]:
        if k in p: return t
    return 'partyvenue'

POINTS = {
 'day': ["Welcome on the shaded porch","Games and activities on the lawn","Lunch, then pool time","Sunset photos on the deck"],
 'evening': ["Golden-hour arrivals on the lawn","Dinner and toasts on the deck","Dance floor till 10 pm","Stay over in three bedrooms"],
 'ceremony': ["Décor and mandap on the lawn","Rituals with family on the porch","Lunch or dinner on the lawn","Portraits by the pool"],
 'stay': ["Check in, pool afternoon","Dinner under the sky","Three bedrooms for the night","Slow breakfast on the porch"],
 'shoot': ["Pool reflections","Palm-lined deck","Red-roof cottage","Wide shots from the terrace"],
 'tour': ["Private pool with kids' section","Lawn for up to 150 guests","Pool deck, terrace and porch","Three bedrooms"],
 'guide': ["Plan the flow early","Zone the lawn, porch and deck","Music till 10 pm","Ask us for a quote"],
}
PATH_PTS = {
 '/mata-ki-chowki-jagran-venue-noida/': ["Darbar and décor on the lawn","Bhajans with the family","Bhog and langar on the lawn","Elders seated on the porch"],
 '/corporate-party-farmhouse-noida/': ["Strategy session on the porch","Team games on the lawn","Lunch under the sky","Awards at sunset"],
 '/team-outing-places-in-noida/': ["Workshop on the porch","Cricket on the lawn","Lunch under the sky","Pool time after"],
 '/workshop-venue-in-noida/': ["Sessions on the shaded porch","Breakout circles on the lawn","Working lunch","Wind-down by the pool"],
 '/product-launch-venue-noida/': ["Stage and screen on the lawn","Guests welcomed on the porch","Dinner on the deck","Wraps by 10 pm"],
 '/film-shooting-location-in-noida/': ["Pool and palm frames","Red-roof cottage exteriors","Lawn wide shots","Rooms for the crew"],
}
POINT_TITLE = {'day':'How the day flows','evening':'How the evening flows','ceremony':'How the function flows',
               'stay':'How the stay flows','shoot':'Frames to shoot','tour':'The property','guide':'The checklist'}

Q = {
 'day': ["Lawn games or pool games: which wins in your group?","Who is the first person you'd invite?","Morning plan or afternoon plan?","Which corner would you claim first: lawn, porch or deck?","Tag the friend who always plans the day out."],
 'evening': ["What's on your 7-to-10 pm playlist?","Sunset dinner or poolside snacks?","Who's the first on the dance floor in your group?","Fairy lights or candles?","Who stays over when the music stops?"],
 'ceremony': ["Lawn or porch for the rituals?","What's the one tradition your family never skips?","Morning muhurat or evening?","Marigold or white florals?","How many guests on your list right now?"],
 'stay': ["Pool first or nap first?","Who gets the first bedroom in your group?","Breakfast on the porch or brunch by the pool?"],
 'shoot': ["Golden hour or blue hour?","Pool frame or palm frame?","Which shot would you post first?"],
 'tour': ["Which spot would you book this for?","Pool, lawn or terrace: your favourite?","What would you host here first?"],
 'guide': ["Save this for your next party.","Bookmark this for later.","Send this to whoever is planning your next function."],
}

def build():
    start = dt.date(2026, 11, 15); end = dt.date(2027, 5, 15)
    calmap = {}
    for p in cal:
        d = dt.datetime.strptime(p['date'], '%d/%m/%Y').date()
        lines = p['text'].split('\n')
        calmap[d] = dict(kicker=p['kicker'], head=p['headline'], en=p.get('sub',''), body=' '.join(l for l in lines[1:] if not l.lower().startswith('tap book')).strip(),
                         first=lines[0], path=p['path'], photo=p['photo'])
    for e in extra:
        d = dt.datetime.strptime(e['id'][1:], '%Y%m%d').date()
        en, body, path = EXTRA_BODY[e['id']]
        calmap[d] = dict(kicker=e['kicker'], head=e['headline'], en=en, body=body, first='', path=path, photo=e['photo'])
    for (md, kick, head, en, body, typ, path, photo) in B:
        m, dd = map(int, md.split('-'))
        d = dt.date(2027, m, dd)
        calmap[d] = dict(kicker=kick, head=head, en=en, body=body, first='', path=path, photo=photo, typ=typ, md=md)
    days = []
    d = start; i = 0
    FMT = ['reel','carousel','reel','single','reel','carousel','reel']
    while d <= end:
        t = calmap[d]
        typ = t.get('typ') or typ_of(t['path'], t['kicker'])
        fmt = FMT[d.weekday()]
        pts = G.get(t.get('md',''), None) or PATH_PTS.get(t['path']) or POINTS[typ]
        guide = typ == 'guide' or t.get('md') in G
        if fmt == 'reel':
            vt = 'tour' if typ == 'tour' else ('guide' if guide else ('hook' if i % 2 == 0 else 'trio'))
        elif fmt == 'carousel':
            vt = 'guide'
        else:
            vt = 'tour' if i % 3 != 1 else 'trio'
        k = kw(t['path']); tag = tag_of(t['path'], typ)
        uid = 'n' + d.strftime('%Y%m%d')
        days.append(dict(id=uid, date=d.isoformat(), dow=d.strftime('%a'), fmt=fmt, vt=vt, typ=typ, guide=guide,
                         kicker=t['kicker'], head=t['head'], en=t['en'], body=t['body'], first=t['first'], path=t['path'],
                         photo=t['photo'], kw=k, tag=tag, points=pts, ptitle=('The checklist' if guide else POINT_TITLE[typ]), qi=i))
        d += dt.timedelta(days=1); i += 1
    return days

def hashtags(x):
    return ['#farmhouseinnoida', '#noidafarmhouse', '#' + x['tag'], '#noidaevents', '#delhincr']

def ig_caption(x):
    ev = x['typ'] in ('evening',) or 'cocktail' in x['path'] or 'new-year' in x['path']
    L = [f"{x['kw']} | {x['head']} ✨", '']
    if x['first']: L.append(x['first'])
    L.append(x['body'])
    if x['fmt'] == 'carousel': L += ['', 'Swipe through ➝ and save it for later.']
    L += ['', "✦ Private pool with kids' section · Lawn for up to 150 · 3 bedrooms",
          '✦ Music till 10 pm' + (' · FL-11 licence needed if liquor is served' if ev else ' · One group at a time'),
          '📍 Sector 135, Noida · beside the Noida–Greater Noida Expressway',
          f'📞 Call / WhatsApp {PHONE} · or DM “DATE” for a quote', '', ' '.join(hashtags(x))]
    return '\n'.join(L)

def fb_caption(x):
    L = [f"{x['head']} ✨", '']
    if x['first']: L.append(x['first'])
    L += [x['body'], '', f"📍 Sector 135, Noida (beside the Noida–Greater Noida Expressway)",
          f'📞 {PHONE}', f"👉 {SITE}{x['path']}?utm_source=facebook&utm_medium=social&utm_campaign={x['id']}", '',
          '#FarmhouseInNoida #' + x['tag']]
    return '\n'.join(L)

def yt(x):
    t = f"{x['head']} | {x['kw']}"
    if len(t) > 70: t = x['kw'] if len(x['kw']) <= 70 else x['kw'][:70]
    desc = '\n'.join([f"{x['en']}." if x['en'] and not x['en'].endswith('.') else x['en'], x['body'], '',
        '📍 Sector 135, Noida, beside the Noida–Greater Noida Expressway', f'📞 Call / WhatsApp {PHONE}',
        f"🌐 {SITE}{x['path']}?utm_source=youtube&utm_medium=shorts&utm_campaign={x['id']}", '',
        f"#Shorts #FarmhouseInNoida #{x['tag']} #Noida"])
    tags = [x['kw'].lower(), 'farmhouse in noida', 'noida farmhouse party', 'party venue noida', x['tag'], 'sector 135 noida']
    return t, desc, tags

def threads(x):
    q = Q[x['typ'] if not x['guide'] else 'guide'][x['qi'] % len(Q[x['typ'] if not x['guide'] else 'guide'])]
    if x['guide']:
        s = f"{x['en']}:\n\n" + '\n'.join('• ' + p for p in x['points']) + f"\n\n{q}"
    elif x['first']:
        s = f"{x['first']}\n\n{x['body']}\n\n{q}"
    elif x['typ'] == 'tour':
        s = f"{x['head']}.\n\n{x['body']}\n\n{q}"
    else:
        s = f"{x['head']} {('— ' + x['en']) if x['en'] else ''}\n\n{x['body']}\n\n{q}"
    if len(s) > 480: s = s[:477].rsplit(' ', 1)[0] + '…'
    return s

if __name__ == '__main__':
    days = build()
    for x in days:
        x['ig'] = ig_caption(x); x['fb'] = fb_caption(x)
        x['yt_title'], x['yt_desc'], x['yt_tags'] = yt(x)
        x['threads'] = threads(x)
        x['alt'] = f"{x['kw']}: {x['en'] or x['head']} at Noida Farmhouse Party, a private pool farmhouse in Sector 135, Noida."
    json.dump(days, open(os.path.join(ROOT,'content','plan.json'), 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(days), Counter(x['fmt'] for x in days), Counter(x['vt'] for x in days))
    print(max(len(x['ig']) for x in days), max(len(x['threads']) for x in days), max(len(x['yt_title']) for x in days))
    for x in days[:3] + days[95:97]: print('----', x['date'], x['fmt'], x['vt'], '\n', x['ig'], '\n>>', x['yt_title'], '\n>>', x['threads'])
