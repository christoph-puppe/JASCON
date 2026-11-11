import sys, json, os, re
sys.path.insert(0, sys.argv[1])
from cacenv import CacEnv
from lxml import etree
root=sys.argv[2]
env=CacEnv(root)
r=json.load(open(sys.argv[3]))['rules']
for rid in sys.argv[4].split(','):
    v=r[rid]
    t=env.render_file(os.path.join(root,v['static_oval_file']),{"rule_id":rid,"rule_title":v['title'],"products":{"ubuntu2404"}})
    m=re.search(r'<definition[^>]*id="%s".*?</definition>'%re.escape(rid), t, re.S)
    txt=m.group(0) if m else t[:1500]
    txt=re.sub(r'<metadata>.*?</metadata>','',txt,flags=re.S)
    txt=re.sub(r'\n\s*\n','\n',txt)
    print("=====",rid, "|", v['title']); print(txt[:1800])
