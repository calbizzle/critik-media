from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
B='/workspace/rateit/public/brand/'; R='/workspace/rateit/public/ranks/'
FV='/usr/share/fonts/truetype/sand-box/google/Inter Tight/InterTight-VariableFont_wght.ttf'
def F(sz,w=b'Bold'):
    f=ImageFont.truetype(FV,sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
G=[(245,166,35),(230,62,122),(139,92,246)]; ACC=(242,116,90)
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def grad(w,h):
    g=Image.new('RGB',(w,1))
    for x in range(w):
        t=x/(w-1); g.putpixel((x,0), lerp(G[0],G[1],t*2) if t<.5 else lerp(G[1],G[2],(t-.5)*2))
    return g.resize((w,h))
def bg(W,H,photo=None):
    if photo:
        p=Image.open(photo).convert('RGB'); s=max(W/p.width,H/p.height)
        p=p.resize((int(p.width*s)+1,int(p.height*s)+1),Image.LANCZOS)
        p=p.crop(((p.width-W)//2,(p.height-H)//2,(p.width-W)//2+W,(p.height-H)//2+H))
        sh=Image.new('RGB',(W,H),(10,10,14)); m=Image.new('L',(W,H))
        d=ImageDraw.Draw(m)
        for y in range(H): d.line([(0,y),(W,y)],fill=int(150+90*abs(y/H-.45)*2) if y/H<.45 or y/H>.75 else 120)
        return Image.composite(sh,p,m)
    im=Image.new('RGB',(W,H),(13,13,18))
    glow=grad(W,H).resize((W,H)); m=Image.new('L',(W,H)); d=ImageDraw.Draw(m)
    d.ellipse((-W*.3,-H*.25,W*1.3,H*.35),fill=70); m=m.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(glow,im,m)
def gtext(im,xy,txt,f):
    d=ImageDraw.Draw(im); bb=d.textbbox(xy,txt,font=f)
    m=Image.new('L',im.size); ImageDraw.Draw(m).text(xy,txt,font=f,fill=255)
    im.paste(grad(bb[2]-bb[0]+2,1).resize((bb[2]-bb[0]+2,im.height)).crop((0,0,bb[2]-bb[0]+2,im.height)),(bb[0],0),m.crop((bb[0],0,bb[2]+2,im.height)))
def wrap(d,t,f,w):
    out=[]
    for para in t.split('\n'):
        line=''
        for wd in para.split(' '):
            tt=(line+' '+wd).strip()
            if d.textlength(tt,font=f)<=w: line=tt
            else: out.append(line); line=wd
        out.append(line)
    return out
def paste(im,path,cx,cy,h,maxw=None):
    a=Image.open(path).convert('RGBA')
    if maxw and a.width*h/a.height>maxw: h=int(maxw*a.height/a.width)
    a=a.resize((int(a.width*h/a.height),h),Image.LANCZOS)
    im.paste(a,(int(cx-a.width/2),int(cy-a.height/2)),a)
def slide(W,H,s,n,tot):
    im=bg(W,H,s.get('photo')); d=ImageDraw.Draw(im); M=90; tall=H>1500
    top=170 if tall else 110
    if s.get('kicker'):
        d.text((M,top),s['kicker'].upper(),font=F(38),fill=ACC); top+=80
    fh=F(s.get('hs',104)); y=top
    lines=wrap(d,s['head'],fh,W-2*M)
    for i,l in enumerate(lines):
        if s.get('gradhead') and i==len(lines)-1: gtext(im,(M,y),l,fh)
        else: d.text((M,y),l,font=fh,fill='white')
        y+=int(fh.size*1.12)
    y+=30
    if s.get('body'):
        fb=F(46,b'Medium')
        for l in wrap(d,s['body'],fb,W-2*M): d.text((M,y),l,font=fb,fill=(225,225,232)); y+=64
    y+=40
    if s.get('imgs'):
        imgs=s['imgs']; area=H-y-(260 if tall else 190); n_=len(imgs)
        if s.get('grid'):
            cols=3 if n_>2 else n_; cw=(W-2*M)/cols; ih=int(min(cw*.75,area*.6))
            for i,(p,lab,sub) in enumerate(imgs):
                cx=M+cw*(i%cols)+cw/2; cy=y+ih/2+20
                paste(im,p,cx,cy,ih)
                for j,(t,f,c) in enumerate([(lab,F(44),'white'),(sub,F(30,b'Medium'),(200,200,210))]):
                    for k,ln in enumerate(wrap(d,t,f,cw-20)):
                        tw=d.textlength(ln,font=f); d.text((cx-tw/2,cy+ih/2+30+j*60+k*38),ln,font=f,fill=c)
        else:
            sz=int(min(area*.8,(W-2*M)/n_*.85));
            for i,p in enumerate(imgs): paste(im,p,M+(W-2*M)/n_*(i+.5),y+area/2,sz,(W-2*M)/n_*.95)
    fy=H-(200 if tall else 120)
    paste(im,B+'app-icon.png',M+32,fy+32,64)
    d.text((M+84,fy+10),'critik',font=F(40),fill='white')
    t=f'{n}/{tot}'; ff=F(32,b'Medium'); d.text((W-M-d.textlength(t,font=ff),fy+16),t,font=ff,fill=(170,170,180))
    im.paste(grad(W,10),(0,H-10))
    return im
