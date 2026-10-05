# sequential: prep needed parts then render, one at a time (avoid VM OOM)
import json,subprocess,sys
C=json.load(open("caps.json"))
for k in sys.argv[1:]:
    c=C[k]; need=[p[5:-4] for p in c["parts"]]+[e[5:-4] for e in c["markets"].values() if e]
    subprocess.run(["python3","prep2.py"]+need)
    subprocess.run(["python3","render_v4.py",k])
    subprocess.run("rm -f prep/*.mp4 prep/*.ok png/*",shell=True)
    open("jlog.txt","a").write(f"DONE {k}\n")
