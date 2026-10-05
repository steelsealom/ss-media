import json,subprocess,os,sys,re
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920; XF=0.35
Y=(247,209,23,255); WH=(255,255,255,255); BK=(0,0,0,255); RED=(229,57,53,255); DRED=(166,25,46,255)
def f(sz):
    fo=ImageFont.truetype("Cairo.ttf",sz); fo.set_variation_by_name('Black'); return fo
def segs(line):
    out=[]
    for m in re.finditer(r'\*([^*]+)\*|!([^!]+)!|([^*!]+)',line):
        if m.group(1): out.append((m.group(1),Y))
        elif m.group(2): out.append((m.group(2),RED))
        else: out.append((m.group(3),WH))
    return out
def tw(d,t,fo): b=d.textbbox((0,0),t,font=fo,direction="rtl"); return b[2]-b[0]
def wrap(d,text,fo,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if tw(d,re.sub(r'[*!]','',t),fo)>maxw and cur: lines.append(cur); cur=w
        else: cur=t
    lines.append(cur); return lines
def caption(text,path,sz=80,stroke=10,maxw=980,cy=1300):
    fo=f(sz); lh=int(sz*1.35); img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    lines=wrap(d,text,fo,maxw); y0=cy-lh*len(lines)//2
    for i,line in enumerate(lines):
        y=y0+i*lh; sg=segs(line); widths=[tw(d,s,fo) for s,_ in sg]; x=W//2+sum(widths)//2
        for (s,c),w in zip(sg,widths):
            x-=w; d.text((x,y),s,font=fo,fill=c,direction="rtl",stroke_width=stroke,stroke_fill=BK)
    img.save(path)
def card(line,path):
    img=Image.new("RGBA",(W,H),(8,8,8,255)); d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,16],fill=DRED); d.rectangle([0,H-16,W,H],fill=DRED)
    fo=f(84); b=d.textbbox((0,0),line,font=fo,direction="rtl"); d.text((W//2-(b[2]-b[0])//2-b[0],780-b[1]),line,font=fo,fill=Y,direction="rtl")
    fo=f(72); t="الرابط في البايو"; b=d.textbbox((0,0),t,font=fo,direction="rtl"); d.text((W//2-(b[2]-b[0])//2-b[0],940-b[1]),t,font=fo,fill=WH,direction="rtl")
    fo=f(46); t="Steel Seal"; b=d.textbbox((0,0),t,font=fo); d.text((W//2-(b[2]-b[0])//2-b[0],1090-b[1]),t,font=fo,fill=(187,187,187,255))
    img.save(path)
ENC="-c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -ar 48000"
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]).decode().strip())
def mkcard(mk):
    line={"SA":"اطلب الآن من الموقع","OM":"احجز أو اطلب من الموقع"}.get(mk,"اطلب الآن من الموقع")
    if not os.path.exists(f"card{mk}.mp4"):
        card(line,f"card{mk}.png")
        subprocess.run(f"ffmpeg -y -nostdin -hide_banner -loglevel error -loop 1 -t 2.5 -i card{mk}.png -f lavfi -t 2.5 -i anullsrc=r=48000:cl=stereo -vf fps=30,format=yuv420p {ENC} -shortest card{mk}.mp4",shell=True,check=True)
    return f"card{mk}.mp4"
def build(parts,caps,ending,endcaps,usecard,mk,out):
    files=list(parts); durs=[dur(p) for p in parts]
    cum=[]; c=0.0
    for d in durs: cum.append(c); c+=d
    body=c
    allcaps=list(caps)
    if ending:
        files.append(ending); ed=dur(ending); cum.append(body); durs.append(ed)
        allcaps+=[[body+a,body+b,t] for a,b,t in (endcaps or [])]
    if usecard:
        files.append(mkcard(mk)); cum.append(sum(durs)); durs.append(2.5)
    starts=[]; t=0.0
    for d in durs: starts.append(t); t+=d-XF
    total=t+XF
    def remap(tt):
        i=max(j for j in range(len(cum)) if tt>=cum[j]-1e-6)
        return max(starts[i]+0.05, starts[i]+(tt-cum[i]))
    ov=[]; os.makedirs("png",exist_ok=True)
    for i,(a,b,tx) in enumerate(allcaps):
        p=f"png/{os.path.basename(out)}_{i}.png"; caption(tx,p); ov.append((p,remap(a),remap(b)))
    n=len(files); cmd=["ffmpeg","-y","-nostdin","-hide_banner","-loglevel","error","-threads","3"]
    for x in files: cmd+=["-i",x]
    for p,_,_ in ov: cmd+=["-i",p]
    fc=""; cv="[0:v]"; ca="[0:a]"; off=0.0
    for i in range(1,n):
        off+=durs[i-1]-XF
        fc+=f"{cv}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[xv{i}];{ca}[{i}:a]acrossfade=d={XF}[xa{i}];"; cv=f"[xv{i}]"; ca=f"[xa{i}]"
    cur=cv
    for k,(p,a,b) in enumerate(ov):
        yy=f"45*max(0\\,1-(t-{a:.2f})/0.2)"
        fc+=f"{cur}[{n+k}:v]overlay=0:{yy}:enable='between(t,{a:.2f},{b:.2f})'[o{k}];"; cur=f"[o{k}]"
    fc+=f"{cur}null[v];{ca}anull[a]"
    cmd+=["-filter_complex",fc,"-map","[v]","-map","[a]"]+ENC.split()+["-movflags","+faststart",out]
    subprocess.run(cmd,check=True)
    return remap,total
C=json.load(open("caps.json"))
def upload(name,path):
    import time
    if os.path.getsize(path)>49_000_000:
        tmp=path+".s.mp4"; subprocess.run(f"ffmpeg -y -nostdin -hide_banner -loglevel error -i {path} -c:v libx264 -preset veryfast -crf 25 -pix_fmt yuv420p -c:a copy -movflags +faststart {tmp}",shell=True,check=True); os.replace(tmp,path)
    url=""
    for _ in range(5):
        r=subprocess.run(["curl","-s","-m","300","-F","files[]=@"+path,"https://uguu.se/upload"],capture_output=True,text=True).stdout
        try: url=json.loads(r)["files"][0]["url"]; break
        except Exception: pass
        time.sleep(15)
    if not url: url="FAIL"
    open("rlog.txt","a").write(f"URL {name} {url} {os.path.getsize(path)}\n")
    subprocess.run(["python3","push.py","rlog.txt"],capture_output=True)
    if url!="FAIL": os.remove(path)
os.makedirs("out",exist_ok=True)
done=set(l.split()[1] for l in open("rlog.txt") if l.startswith("URL") and l.split()[2].startswith("https://")) if os.path.exists("rlog.txt") else set()
for k in sys.argv[1:]:
    c=C[k]
    for mk,ending in c["markets"].items():
        name=f"{mk}_{k}"; outf=f"out/{name}.mp4"
        if name in done: continue
        build(c["parts"],c["caps"],ending,(c.get("endcaps") or {}).get(mk),c.get("card",True),mk,outf)
        upload(name,outf)
