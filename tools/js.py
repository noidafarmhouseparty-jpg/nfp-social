import os
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, sys
d = {x['id']: x for x in json.load(open(os.path.join(ROOT,'content','plan.json')))}
def cap(i):
    return d[i]['ig'].replace('📞 Call', '🌐 noidafarmhouseparty.com\n📞 Call')
def paste_js(text):
    return ("(()=>{const T=%s;const el=[...document.querySelectorAll('[contenteditable=true]')].find(e=>e.offsetParent);"
            "if(!el) return 'no editor';el.focus();const dt=new DataTransfer();dt.setData('text/plain',T);"
            "el.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));return el.innerText.length})()") % json.dumps(text, ensure_ascii=False)
if __name__ == '__main__':
    kind, i = sys.argv[1], sys.argv[2]
    if kind == 'ig': print(paste_js(cap(i)))
    elif kind == 'th': print(paste_js(d[i]['threads']))
