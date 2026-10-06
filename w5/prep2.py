import json,subprocess,os,sys
IDS=json.load(open("ids.json"))
ENC="-c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -ar 48000"
GRADE="eq=contrast=1.16:saturation=1.38:gamma=0.93"
os.makedirs("prep",exist_ok=True)
def cache():
    subprocess.run(["curl","-s","-H","Authorization: token "+os.environ["GT"],"-H","Accept: application/vnd.github.raw","-o","pcache.txt","https://api.github.com/repos/steelsealom/ss-media/contents/w5/pcache.txt"])
    d={}
    if os.path.exists("pcache.txt"):
        for l in open("pcache.txt"):
            p=l.split()
            if len(p)==2: d[p[0]]=p[1]
    return d
for k in sys.argv[1:]:
    pp=f"prep/{k}.mp4"
    if os.path.exists(pp+".ok"): continue
    C=cache()
    if k in C:
        subprocess.run(["curl","-sL","-o",pp,C[k]])
        if os.path.exists(pp) and os.path.getsize(pp)>100000:
            open(pp+".ok","w").write("1"); print("cache",k,flush=True); continue
    w=json.load(open(f"words/{k}.json")); s=w["s"]; d=w["dur"]; raw=f"raw_{k}.bin"
    subprocess.run(["curl","-sL","-o",raw,f"https://drive.usercontent.google.com/download?id={IDS[k]}&export=download&confirm=t"])
    if os.path.getsize(raw)<100000: print("QUOTA",k,flush=True); sys.exit(3)
    if k=="W5S04": subprocess.run(f"ffmpeg -y -loglevel error -i {raw} -vn -ac 1 -ar 16000 s4.wav",shell=True)
    subprocess.run(f'ffmpeg -y -nostdin -hide_banner -loglevel error -threads 3 -ss {s:.3f} -t {d:.3f} -i {raw} -vf "scale=1080:1920,fps=30,setsar=1,{GRADE}" -af aresample=48000 {ENC} {pp}',shell=True,check=True)
    os.remove(raw); open(pp+".ok","w").write("1")
    r=subprocess.run(["curl","-s","-m","300","-F","files[]=@"+pp,"https://uguu.se/upload"],capture_output=True,text=True).stdout
    try:
        u=json.loads(r)["files"][0]["url"]; C=cache(); C[k]=u
        open("pcache.txt","w").write("".join(f"{a} {b}\n" for a,b in C.items())); subprocess.run(["python3","push.py","pcache.txt"],capture_output=True)
    except Exception: pass
    print("prep",k,flush=True)
