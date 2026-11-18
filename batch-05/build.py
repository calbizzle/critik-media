#!/usr/bin/env python3
"""Batch 05: rate-a-movie reel, Insider medal + rank-up, mates vs stars."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *

P = os.path.dirname(os.path.abspath(__file__))
FOOT = '/workspace/critik-social/footage'
DARK = '0x0d0d12'

def run(cmd):
    print('+', ' '.join(cmd) if isinstance(cmd, list) else cmd)
    subprocess.check_call(cmd)

def card(path, slidespec):
    slide(1080, 1920, slidespec, 1, 1).save(path)
    return path

def png_to_vid(png, out, dur, fps=30):
    run([
        'ffmpeg', '-y', '-loop', '1', '-i', png, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', str(dur), '-r', str(fps),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-vf', f'fps={fps},format=yuv420p,setsar=1',
        '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out
    ])

def trim_pad(src, out, start, end):
    # 1080x1920 letterbox, silent audio, 30fps
    vf = (
        f"trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"scale=1080:1920:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color={DARK},"
        f"fps=30,format=yuv420p,setsar=1"
    )
    run([
        'ffmpeg', '-y', '-i', src, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
        '-vf', vf, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out
    ])

def concat(parts, out):
    lst = os.path.join(P, '_concat.txt')
    with open(lst, 'w') as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart', out
    ])
    os.remove(lst)

# ---------- slides (stories + Sat carousel) ----------
posts = {
    'post-1': [  # rate a movie — story uses slide 1
        dict(kicker='App demo', head='Rate a movie in 10 seconds.', gradhead=1, hs=110),
        dict(kicker='The flow', head='Title. Score. One reason.', gradhead=1, body="Pick what you watched, drop a score out of 10, and say why. 'It was good' is not a reason."),
        dict(kicker='Then your mates see it', head='That is the whole point.', gradhead=1, body='Your ratings land with the people whose taste you actually trust. They can agree, argue, or steal the rec.'),
        dict(kicker='Watch it. Eat it. Rate it.', head='Sign up for the Android test.', gradhead=1, body='The sign-up is on our Insta @critik.app.', imgs=[B+'logo-gradient-banner.png']),
    ],
    'post-2': [  # Insider medal — story uses slide 1
        dict(kicker='Medal reveal 2 of 6', head='Meet the Insider.', gradhead=1, hs=110, imgs=[R+'insider.png']),
        dict(kicker='How to earn it', head='20 followers or 30 likes + comments.', gradhead=1, hs=92, body='Either one gets you there. Ranks are worked out live from your mates and the love your ratings get.'),
        dict(kicker='Earned, not bought', head='Rookie was just the start.', gradhead=1, body='Every profile starts as a Critic in Training. Rookie comes first. Insider is next. Then the climb gets serious.'),
        dict(kicker='Next up: Critik', head='Four more ranks to Icon.', gradhead=1, body='Rate what you watch and eat, and let your mates push you up. Sign up for the Android test on our Insta @critik.app.', imgs=[R+'critik.png', R+'specialist.png', R+'icon.png']),
    ],
    'post-3': [  # mates vs strangers — TikTok carousel + story slide 1
        dict(kicker='Hot take', head="Your mate's 9/10 beats a stranger's 5 stars.", gradhead=1, hs=96),
        dict(kicker="Here's why", head='Your friends already know your taste.', gradhead=1, hs=92, body='A 5-star average is a pile of strangers. Your mate\'s 9/10 already accounts for the fact they cried at a cartoon and still made you watch it.'),
        dict(kicker="That's Critik", head='Rate with the people you actually trust.', gradhead=1, body='Films, shows and eats, scored with your mates. You see their ratings, they see yours, and the argument is half the fun.'),
        dict(kicker='Watch it. Eat it. Rate it.', head='Sign up for the Android test.', gradhead=1, body='The sign-up is on our Insta @critik.app.', imgs=[B+'logo-gradient-banner.png']),
    ],
}

for k, sl in posts.items():
    for plat, (W, H) in {'ig': (1080, 1350), 'tiktok': (1080, 1920)}.items():
        os.makedirs(f'{P}/{k}/{plat}', exist_ok=True)
        for i, s in enumerate(sl, 1):
            slide(W, H, s, i, len(sl)).save(f'{P}/{k}/{plat}/slide-{i}.png')

# ---------- videos ----------
os.makedirs(f'{P}/post-1/video', exist_ok=True)
os.makedirs(f'{P}/post-2/video', exist_ok=True)

# Title/end cards for videos (full 9:16, no slide counter clutter: use slide() anyway for brand consistency)
card(f'{P}/post-1/video/title.png', dict(kicker='App demo', head='Rate a movie in 10 seconds.', gradhead=1, hs=110))
card(f'{P}/post-1/video/end.png', dict(kicker='Watch it. Eat it. Rate it.', head='One title. One score. One reason.', gradhead=1, hs=96, body='Your mates see it on Critik.'))
card(f'{P}/post-2/video/title.png', dict(kicker='Medal reveal 2 of 6', head='Meet the Insider.', gradhead=1, hs=110, imgs=[R+'insider.png']))
card(f'{P}/post-2/video/end.png', dict(kicker='How to earn it', head='20 followers or 30 likes + comments.', gradhead=1, hs=92, body='Earned, not bought. Next up: Critik.'))

# Temporary clips
tmp = f'{P}/_tmp'
os.makedirs(tmp, exist_ok=True)
png_to_vid(f'{P}/post-1/video/title.png', f'{tmp}/rate-title.mp4', 1.4)
# Trim 0.00-10.30: full rating flow + loading; cut before Maya Chen feed
trim_pad(f'{FOOT}/video-rate-a-movie.mp4', f'{tmp}/rate-body.mp4', 0.00, 10.30)
png_to_vid(f'{P}/post-1/video/end.png', f'{tmp}/rate-end.mp4', 2.4)
concat([f'{tmp}/rate-title.mp4', f'{tmp}/rate-body.mp4', f'{tmp}/rate-end.mp4'], f'{P}/post-1/video/rate-a-movie.mp4')

png_to_vid(f'{P}/post-2/video/title.png', f'{tmp}/rank-title.mp4', 2.0)
# Trim 1.00-4.70: Rookie badge into Insider celebration; skip demo personas on either side
trim_pad(f'{FOOT}/video-rank-up.mp4', f'{tmp}/rank-body.mp4', 1.00, 4.70)
png_to_vid(f'{P}/post-2/video/end.png', f'{tmp}/rank-end.mp4', 3.0)
concat([f'{tmp}/rank-title.mp4', f'{tmp}/rank-body.mp4', f'{tmp}/rank-end.mp4'], f'{P}/post-2/video/rank-up-insider.mp4')

# Story stills (tiktok slide-1 already built). Also export a 9:16 story folder alias.
# Preview strip of first slides + video title cards
from PIL import Image
thumbs = [
    f'{P}/post-1/tiktok/slide-1.png',
    f'{P}/post-2/tiktok/slide-1.png',
    f'{P}/post-3/tiktok/slide-1.png',
    f'{P}/post-3/tiktok/slide-2.png',
    f'{P}/post-3/tiktok/slide-3.png',
    f'{P}/post-3/tiktok/slide-4.png',
]
ims = [Image.open(t).convert('RGB').resize((270, 480), Image.LANCZOS) for t in thumbs]
sheet = Image.new('RGB', (270*len(ims)+20*(len(ims)+1), 520), (13,13,18))
for i, im in enumerate(ims):
    sheet.paste(im, (20+i*(270+20), 20))
sheet.save(f'{P}/preview.png')

# cleanup temp clips
import shutil
shutil.rmtree(tmp, ignore_errors=True)
print('OK')
