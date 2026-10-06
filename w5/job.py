import json,subprocess,sys
C=json.load(open("caps.json"))
for k in sys.argv[1:]:
    c=C[k]
    done=set(l.split()[1] for l in open("rlog.txt") if l.startswith("URL") and l.split()[2].startswith("https://"))
    if all(f"{m}_{k}" in done for m in c["markets"]): continue
    need=[p[5:-4] for p in c["parts"]]+[e[5:-4] for e in c["markets"].values() if e]
    if subprocess.run(["python3","prep2.py"]+need).returncode==3: break
    subprocess.run(["python3","render_v4.py",k])
    subprocess.run("rm -f prep/*.mp4 prep/*.ok png/*",shell=True)
