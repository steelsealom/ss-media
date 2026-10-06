import sys,base64,json,subprocess,time,os
T=os.environ["GT"]
for f in sys.argv[1:]:
    url=f"https://api.github.com/repos/steelsealom/ss-media/contents/w5/{f}"
    H=["-H","Authorization: token "+T]
    g=subprocess.run(["curl","-s"]+H+[url],capture_output=True,text=True).stdout
    try: sha=json.loads(g).get("sha")
    except Exception: sha=None
    d={"message":"w5 "+f,"content":base64.b64encode(open(f,"rb").read()).decode()}
    if sha: d["sha"]=sha
    open("/tmp/pd.json","w").write(json.dumps(d))
    r=subprocess.run(["curl","-s","-o","/dev/null","-w","%{http_code}","-X","PUT"]+H+[url,"--data-binary","@/tmp/pd.json"],capture_output=True,text=True).stdout
    print(f,r); time.sleep(1)
