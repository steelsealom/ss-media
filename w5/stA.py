import json,subprocess,os,re,base64,urllib.request
from concurrent.futures import ThreadPoolExecutor
IDS=json.load(open("ids.json")); os.makedirs("words",exist_ok=True)
TOK=os.environ["GT"]
def have(k):
    r=subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","-H","Authorization: token "+TOK,f"https://api.github.com/repos/steelsealom/ss-media/contents/w5/words/{k}.json"],capture_output=True,text=True).stdout
    return r=="200"
def put(local,remote):
    api=f"https://api.github.com/repos/steelsealom/ss-media/contents/{remote}"
    h={"Authorization":f"token {TOK}","User-Agent":"ss"}; sha=None
    try:
        with urllib.request.urlopen(urllib.request.Request(api,headers=h)) as r: sha=json.load(r)["sha"]
    except Exception: pass
    body={"message":"w5 "+remote,"content":base64.b64encode(open(local,"rb").read()).decode()}
    if sha: body["sha"]=sha
    with urllib.request.urlopen(urllib.request.Request(api,data=json.dumps(body).encode(),method="PUT",headers={**h,"Content-Type":"application/json"})) as r: return r.status
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]).decode().strip())
def bounds(p):
    out=subprocess.run(["ffmpeg","-vn","-i",p,"-af","silencedetect=n=-32dB:d=0.35","-f","null","-"],capture_output=True,text=True).stderr
    D=dur(p); s=0.0; e=D
    ev=[(k,float(v)) for k,v in re.findall(r"silence_(start|end): ([\d.]+)",out)]
    if ev and ev[0][0]=="start" and ev[0][1]<0.05 and len(ev)>1 and ev[1][0]=="end": s=max(0,ev[1][1]-0.25)
    if ev and ev[-1][0]=="start" and ev[-1][1]>D-0.05-1: e=min(D,ev[-1][1]+0.35) if D-ev[-1][1]>0.6 else D
    return s,e
def get(k):
    if os.path.exists(f"w_{k}.wav"): return k
    raw=f"raw_{k}.bin"
    for _ in range(3):
        subprocess.run(["curl","-sL","-o",raw,f"https://drive.usercontent.google.com/download?id={IDS[k]}&export=download&confirm=t"])
        if os.path.exists(raw) and os.path.getsize(raw)>100000: break
    s,e=bounds(raw)
    subprocess.run(["ffmpeg","-y","-nostdin","-loglevel","error","-ss",f"{s:.3f}","-to",f"{e:.3f}","-i",raw,"-vn","-ac","1","-ar","16000",f"w_{k}.wav"])
    json.dump([s,e-s],open(f"b_{k}.json","w")); os.remove(raw); return k
todo=[k for k in IDS if not have(k)]
print("todo",len(todo),flush=True)
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=6)
with ThreadPoolExecutor(3) as ex:
    for k in ex.map(get,todo):
        segs,_=m.transcribe(f"w_{k}.wav",language="ar",word_timestamps=True,vad_filter=True,beam_size=2)
        s,d=json.load(open(f"b_{k}.json"))
        words=[[round(w.start,2),round(w.end,2),w.word.strip()] for sg in segs for w in sg.words]
        json.dump({"dur":round(d,3),"s":round(s,3),"words":words},open(f"words/{k}.json","w"),ensure_ascii=False)
        print("w",k,put(f"words/{k}.json",f"w5/words/{k}.json"),flush=True)
print("ALL DONE",flush=True)
