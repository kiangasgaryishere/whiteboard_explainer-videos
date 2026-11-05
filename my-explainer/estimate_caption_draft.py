"""Generate explicitly UNVERIFIED word-caption timing from the supplied transcript.
Line anchors are inferred from script order and observed pauses, not speech recognition.
Within each line, word lengths distribute time over voiced regions. Review required.
"""
from pathlib import Path
import hashlib,json,re,subprocess
P=Path(__file__).parent
lines=[s.strip().lstrip('- ') for s in (P/'transcript.md').read_text().splitlines() if s.strip()]
anchors=[(0,4.192018),(4.895034,6.878617),(7.517234,9.522812),(10.070249,12.384558),(13.011179,15.874399),(16.379048,22.843107),(23.329478,25.033605),(25.417143,31.638821),(32.064898,34.354717),(34.746259,38.456009),(38.868685,42.349524),(42.779773,44.096916),(44.566961,46.29068),(46.71483,49.237982),(49.570023,52.998707),(53.398549,55.429478),(55.870816,57.33195),(57.794853,60.304172),(60.765714,61.868844),(62.305828,63.926077),(64.338503,65.371111),(65.752154,66.85644),(67.219841,71.13161),(71.533107,83.33102),(83.73,90.070317),(90.485397,93.088458)]
assert len(lines)==len(anchors)
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(P/'source.mp3'),'-af','silencedetect=noise=-34dB:d=0.18','-f','null','-'],capture_output=True,text=True,check=True)
silences=[];start=None
for line in r.stderr.splitlines():
 m=re.search(r'silence_start: ([\d.]+)',line)
 if m:start=float(m.group(1))
 m=re.search(r'silence_end: ([\d.]+)',line)
 if m and start is not None:silences.append((start,float(m.group(1))));start=None
words=[]
for n,(text,(a,b)) in enumerate(zip(lines,anchors)):
 voiced=[];cur=a
 for sa,sb in silences:
  if sb<=a or sa>=b:continue
  if sa>cur:voiced.append((cur,min(sa,b)))
  cur=max(cur,sb)
 if cur<b:voiced.append((cur,b))
 span=sum(y-x for x,y in voiced)
 def time_at(v):
  for x,y in voiced:
   if v<=y-x:return x+max(0,v)
   v-=y-x
  return b
 tokens=text.split();weights=[max(1,len(re.sub(r'[^\w]','',w)))**.6 for w in tokens];total=sum(weights);pos=0
 for token,w in zip(tokens,weights):
  st=time_at(span*pos/total);pos+=w;en=time_at(span*pos/total)
  words.append({'start':round(st,6),'end':round(en,6),'text':token,'line':n})
meta={'reviewed':False,'timing_status':'estimated-draft','method':'Inferred line anchors from observed pauses; weighted word durations over voice activity. NOT ASR or forced alignment.','source_sha256':hashlib.sha256((P/'source.mp3').read_bytes()).hexdigest(),'words':words,'line_anchors':[{'start':a,'end':b,'text':s} for s,(a,b) in zip(lines,anchors)]}
(P/'word-captions.estimated.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(P/'word-captions.estimated.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(w['start'])} --> {stamp(w['end'])}\n{w['text']}" for i,w in enumerate(words))+'\n')
print(len(words),'word cues created; estimated draft, NOT verified synchronization.')
