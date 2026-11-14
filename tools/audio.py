import os
ROOT = os.environ.get('NFP_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, wave
os.makedirs(os.path.join(ROOT, 'tools', 'audio'), exist_ok=True)
SR = 44100; D = 12.0
rng = np.random.default_rng(7)
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def pad(freqs, t, env):
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (det / 12)
            s += np.sin(2*np.pi*ff*t) * 0.6 + 0.25*np.sin(2*np.pi*2*ff*t) + 0.08*np.sin(2*np.pi*3*ff*t)
    return s * env / (len(freqs) * 3)
def pluck(f, n, decay=2.2):
    t = np.arange(n) / SR
    return (np.sin(2*np.pi*f*t) + 0.3*np.sin(2*np.pi*2*f*t) + 0.1*np.sin(2*np.pi*3*f*t)) * np.exp(-t*decay) * np.minimum(1, t*400)
def reverb(x, secs=1.8, mix=0.28):
    n = int(SR*secs); ir = rng.standard_normal(n) * np.exp(-np.arange(n)/SR*3.2); ir /= np.sqrt((ir**2).sum())
    from numpy.fft import rfft, irfft
    L = len(x) + n; N = 1 << (L-1).bit_length()
    w = irfft(rfft(x, N) * rfft(ir, N), N)[:len(x)]
    return (1-mix)*x + mix*w
PROG = [
 ([[60,64,67,71],[57,60,64,67],[53,57,60,64],[55,59,62,67]], 84),   # Cmaj7 Am7 Fmaj7 G
 ([[62,65,69,72],[58,62,65,69],[60,64,67,70],[57,60,64,69]], 78),   # Dm7 Bbmaj7 C7 Am
 ([[57,60,64,67],[53,57,60,64],[48,52,55,59],[55,59,62,65]], 90),   # Am7 Fmaj7 Cmaj7 G7
 ([[64,67,71,74],[60,64,67,71],[62,66,69,72],[59,62,66,69]], 72),   # Em7 Cmaj7 D7 Bm7
 ([[65,69,72,76],[62,65,69,72],[58,62,65,69],[60,64,67,72]], 96),   # Fmaj7 Dm7 Bbmaj7 C
 ([[55,59,62,66],[52,55,59,62],[48,52,55,59],[50,54,57,60]], 80),   # Gmaj7 Em7 Cmaj7 D7
]
for k, (chords, bpm) in enumerate(PROG):
    n = int(SR*D); t = np.arange(n)/SR; out = np.zeros(n)
    seg = n // 4
    for i, ch in enumerate(chords):
        a, b = i*seg, (i+1)*seg if i < 3 else n
        tt = t[a:b] - t[a]; L = b - a
        env = np.minimum(1, tt/0.8) * np.minimum(1, (L/SR - tt)/0.6)
        out[a:b] += 0.55 * pad([note(m-12) for m in ch[:3]] + [note(ch[3])], tt, env)
        out[a:b] += 0.18 * np.sin(2*np.pi*note(ch[0]-24)*tt) * env
    beat = 60/bpm/2
    j = 0; pos = 0.6
    while pos < D - 0.8:
        ch = chords[min(3, int(pos / (D/4)))]
        m = ch[[0,2,1,3,2,1][j % 6]] + 12
        s = int(pos*SR); ln = min(int(SR*1.6), n - s)
        out[s:s+ln] += 0.16 * pluck(note(m), ln) * (0.8 + 0.2*rng.random())
        pos += beat * (2 if j % 4 == 3 else 1); j += 1
    out = reverb(out)
    out *= np.minimum(1, t/0.5) * np.minimum(1, (D - t)/1.2)
    out = out / np.max(np.abs(out)) * 0.6
    st = np.stack([out, np.roll(out, 220)], 1)
    w = wave.open(os.path.join(ROOT,'tools','audio',f'a{k}.wav'), 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
print('ok')
