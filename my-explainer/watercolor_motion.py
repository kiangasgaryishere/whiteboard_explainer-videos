"""Watercolor motion proof. No estimated captions or narration timing.
Use --final only with a reviewed watercolor-edit.json containing scenes and captions.
"""
import sys,json,math,subprocess
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
P=Path(__file__).parent
W,H=1080,1920; FPS=25
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FA='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
final='--final' in sys.argv
narrated_draft='--narrated-draft' in sys.argv
if narrated_draft:
 if final: raise SystemExit('Choose final or narrated draft, not both.')
 # Provisional story beats only; this mode intentionally has no captions.
 boundaries=[('study',0,16.3),('passive',16.3,30.5),('active',30.5,40),('restaurant',40,67),('active',67,71),('package',71,90),('active',90,94)]
 scenes=[{'asset':a,'start':s,'end':e} for a,s,e in boundaries];captions=[]
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'source.mp3'),'-f','s16le','-ar','44100','-ac','1','-'])
 duration=len(raw)/88200
if final:
 edit=json.loads((P/'watercolor-edit.json').read_text()); scenes=edit['scenes'];captions=edit['captions']
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'source.mp3'),'-f','s16le','-ar','44100','-ac','1','-'])
 duration=len(raw)/88200
elif not narrated_draft:
 scenes=[{'asset':a,'start':i*4,'end':(i+1)*4} for i,a in enumerate(['study','passive','active','restaurant','package'])];captions=[];duration=20
# Prepare each art layer and trace actual ink contours. Only motion composition,
# original generated artwork files are preserved unchanged.
cache={}
for s in scenes:
 a=s['asset']
 if a in cache:continue
 src=np.array(Image.open(P/'assets'/f'{a}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 gray=cv2.cvtColor(src,cv2.COLOR_RGB2GRAY)
 dark=np.where(gray<120,255,0).astype('uint8')
 dark[:300]=0;dark[1590:]=0
 contours,_=cv2.findContours(dark,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
 contours=[c for c in contours if cv2.arcLength(c,False)>18]
 contours.sort(key=lambda c:(int(c[:,:,1].mean())//150,int(c[:,:,0].mean())))
 rng=np.random.default_rng(7)
 grain=rng.normal(0,.65,(H,W,1))
 bg=np.clip(np.array([255,246,232])[None,None,:]+grain,0,255).astype('uint8')
 lens=[cv2.arcLength(c,False) for c in contours]
 cache[a]=(src,bg,contours,lens,sum(lens))
out=P/'out'/('narrated-visual-draft.mp4' if narrated_draft else 'my-explainer.mp4' if final else 'watercolor-motion-preview.mp4')
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-']
if final or narrated_draft:cmd+=['-i',str(P/'source.mp3'),'-map','0:v','-map','1:a','-c:a','aac','-b:a','192k','-ar','44100']
cmd+=['-c:v','libx264','-threads','4','-preset','fast','-crf','20','-pix_fmt','yuv420p','-t',str(duration),'-movflags','+faststart',str(out)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
previous=None;finished=np.zeros((H,W),np.uint8);idx=0;spent=0
for f in range(math.ceil(duration*FPS)):
 t=f/FPS;s=next((s for s in scenes if s['start']<=t<s['end']),scenes[-1]);a=s['asset'];age=t-s['start']
 src,bg,contours,lens,total=cache[a]
 if previous is not s:finished.fill(0);idx=0;spent=0;previous=s
 # Reveal outlines before watercolor pigment settles in.
 target=min(1,age/1.65)*total
 while idx<len(contours) and spent+lens[idx]<=target:
  cv2.drawContours(finished,contours,idx,255,2,lineType=cv2.LINE_AA);spent+=lens[idx];idx+=1
 mask=finished.copy()
 if idx<len(contours):
  c=contours[idx];n=max(1,int(len(c)*(target-spent)/max(1,lens[idx])))
  if n>1:cv2.polylines(mask,[c[:n]],False,255,2,lineType=cv2.LINE_AA)
 alpha=mask[:,:,None].astype(np.float32)/255
 ink=np.minimum(src.astype(np.float32),100)
 frame=bg*(1-alpha)+ink*alpha
 fill=max(0,min(1,(age-1.55)/1.2));fill=fill*fill*(3-2*fill)
 frame=frame*(1-fill)+src*fill
 im=Image.fromarray(frame.astype('uint8'));d=ImageDraw.Draw(im)
 if final:
  title=s.get('title','')
  if title:
   font=ImageFont.truetype(F,52);d.text((540,260),title,font=font,anchor='mm',fill='#2369be')
  cue=next((c for c in captions if c['start']<=t<c['end']),None)
  if cue:
   text=cue['text'];rtl=any('\u0600'<=c<='\u06ff' for c in text);font=ImageFont.truetype(FA if rtl else F,43)
   lines=[];line=''
   for word in text.split():
    candidate=(line+' '+word).strip()
    if d.textlength(candidate,font=font)>800 and line:lines.append(line);line=word
    else:line=candidate
   if line:lines.append(line)
   if len(lines)>2:raise ValueError('Split caption into shorter verified cues: '+text)
   h=82+len(lines)*65;cy=1560
   d.rounded_rectangle((90,cy-h/2,990,cy+h/2),radius=25,fill='#243348')
   for j,line in enumerate(lines):d.text((540,cy+(j-(len(lines)-1)/2)*65),line,font=font,anchor='mm',fill='white' if rtl else '#9bc3ff',direction='rtl' if rtl else 'ltr')
 proc.stdin.write(im.tobytes())
 if f%100==0:print(f'{t:.1f}/{duration:.3f}',flush=True)
proc.stdin.close()
if proc.wait():raise SystemExit('FFmpeg failed')
print(out,flush=True)
