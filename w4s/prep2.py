import json,subprocess,os,sys
IDS=json.load(open("ids.json"))
ENC="-c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -ar 48000"
GRADE="eq=contrast=1.16:saturation=1.38:gamma=0.93"
os.makedirs("prep",exist_ok=True)
for k in sys.argv[1:]:
    pp=f"prep/{k}.mp4"
    if os.path.exists(pp+".ok"): continue
    w=json.load(open(f"words/{k}.json")); s=w["s"]; d=w["dur"]; raw=f"raw_{k}.bin"
    for _ in range(3):
        subprocess.run(["curl","-sL","-o",raw,f"https://drive.usercontent.google.com/download?id={IDS[k]}&export=download&confirm=t"])
        if os.path.exists(raw) and os.path.getsize(raw)>100000: break
    subprocess.run(f'ffmpeg -y -nostdin -hide_banner -loglevel error -threads 3 -ss {s:.3f} -t {d:.3f} -i {raw} -vf "scale=1080:1920,fps=30,setsar=1,{GRADE}" -af aresample=48000 {ENC} {pp}',shell=True,check=True)
    os.remove(raw); open(pp+".ok","w").write("1"); print("prep",k,flush=True)
