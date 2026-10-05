import json,os
exec(open("cl4.py",encoding="utf-8").read())
exec(open("ec4.py",encoding="utf-8").read())
W={}
def words(k):
    if k not in W: W[k]=json.load(open(f"words/{k}.json"))
    return W[k]
out={}
for key,c in CLIPS.items():
    parts=c["parts"]
    if not all(os.path.exists(f"words/{p}.json") for p in parts): continue
    off={}; o=0.0
    for p in parts: off[p]=o; o+=words(p)["dur"]
    caps=[]
    for n,(p,i0,i1,tx) in enumerate(c["ch"]):
        w=words(p)["words"]
        i1=min(i1,len(w)); i0=min(i0,len(w)-1)
        a=off[p]+max(0.0,w[i0][0]-0.08)
        b=off[p]+w[i1-1][1]+0.35
        caps.append([a,b,tx])
    for n in range(len(caps)):
        nxt=caps[n+1][0] if n+1<len(caps) else o
        caps[n][1]=round(min(max(caps[n][1],min(nxt,caps[n][1]+1.2)),nxt-0.02 if n+1<len(caps) else o),2)
        caps[n][0]=round(caps[n][0],2)
    ent={"parts":[f"prep/{p}.mp4" for p in parts],"caps":caps,"card":c.get("card",True),
         "markets":{m:(f"prep/{e}.mp4" if e else None) for m,e in c["markets"].items()}}
    ec={}
    for m,e in c["markets"].items():
        if e and e in ENDCAPS:
            ew=words(e)["words"]; lst=[]
            for i0,i1,tx in ENDCAPS[e]:
                i1=min(i1,len(ew)); a=max(0,ew[i0][0]-0.08); b=ew[i1-1][1]+0.6
                lst.append([round(a,2),round(min(b,words(e)["dur"]),2),tx])
            ec[m]=lst
    if ec: ent["endcaps"]=ec
    out[key]=ent
json.dump(out,open("caps.json","w"),ensure_ascii=False,indent=0)
print(len(out))
