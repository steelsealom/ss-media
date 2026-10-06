# needs: export GT=<token>
mkdir -p /home/user/w5/words && cd /home/user/w5
g(){ curl -s -H "Authorization: token $GT" -H "Accept: application/vnd.github.raw" -o "$2" "https://api.github.com/repos/steelsealom/ss-media/contents/$1"; }
for f in cl5a.py cl5b.py cl5c.py ec5.py ids.json rlog.txt mkcaps5.py job.py push5.py; do g w5/$f $f & done
for f in render_v4.py prep2.py; do g w4s/$f $f & done; wait
cp push5.py push.py
for k in $(python3 -c "import json;print(' '.join(json.load(open('ids.json'))))"); do g w5/words/$k.json words/$k.json & done
[ -s Cairo.ttf ] || curl -sL -o Cairo.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf" & wait
python3 mkcaps5.py
