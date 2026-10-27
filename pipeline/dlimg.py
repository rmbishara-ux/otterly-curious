"""dlimg.py E04 : download every ledger image with a url but no shots/<id>.png"""
import json,subprocess,sys,os
ep=sys.argv[1]; d=json.load(open(f'episodes/{ep}/image_ledger.json'))
for k,v in d.items():
    p=f'episodes/{ep}/shots/{k}.png'
    if v.get('url') and not os.path.exists(p):
        r=subprocess.run(['curl','-sS','-f','-o',p,v['url']]); print(k,r.returncode)
