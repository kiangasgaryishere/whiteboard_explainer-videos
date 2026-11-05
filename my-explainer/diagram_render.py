"""Revision 3: complete vector drawings -> marker coloring -> written labels.
No image tracing or raster illustration dissolve. Voice alignment is provisional.
"""
import argparse, math, json, subprocess, bisect
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from caption_style import normalize, font_path, load_cues, caption
P=Path(__file__).parent
W,H,FPS=1080,1920,25
INK='#263446'; BLUE='#336cce'; GREEN='#23846e'; GOLD='#dfaa42'; RED='#d7635d'
FA='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'; EN='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
ap=argparse.ArgumentParser();ap.add_argument('--preview',type=float)
ap.add_argument('--revision',type=int,choices=[3,4,5],default=3)
ap.add_argument('--word-captions',type=Path)
ap.add_argument('--style-still',type=float)
ap.add_argument('--sample-word')
a=ap.parse_args();v4=a.revision>=4;v5=a.revision==5
if a.sample_word and a.style_still is None:ap.error('--sample-word is for a still design sample only')
edit=json.loads((P/'kinetic_edit.json').read_text()); beats=edit['beats']
meta=json.loads((P/f'diagram_v{a.revision}.json').read_text())
if 'short_labels' in meta:
 beats=[[t,title,label] for (t,title,_),label in zip(beats,meta['short_labels'])]
if v5:beats=[[f['start'],f['keyword'],''] for f in meta['frames']]
if v4:beats=[[t,normalize(title),normalize(label)] for t,title,label in beats]
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'source.mp3'),'-ar','44100','-ac','1','-f','s16le','-'])
D=len(raw)/88200;duration=min(a.preview,D) if a.preview else D
word_cues=load_cues(a.word_captions,P/'source.mp3',D) if a.word_captions else []
# Soft stationery grain: no stretched strips, decorative headers or slide numbers.
rng=np.random.default_rng(47);noise=rng.normal(0,.65,(H,W,1))
paper=Image.fromarray(np.uint8(np.clip(np.array([253,250,242])[None,None,:]+noise,0,255)))
if v4:paper=Image.open(P/'assets'/'notebook-paper.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
marker_count=0
class Icon:
 def __init__(self,cx,cy,s=1):self.cx=cx;self.cy=cy;self.s=s;self.paths=[];self.regions=[]
 def point(self,x,y):return(self.cx+x*self.s,self.cy+y*self.s)
 def line(self,pts,w=5,c=INK):self.paths.append(([self.point(x,y) for x,y in pts],c,w))
 def poly(self,pts,fill=None,w=5):
  self.line(pts+[pts[0]],w)
  if fill:self.regions.append(([self.point(x,y) for x,y in pts],fill))
 def box(self,x,y,w,h,fill=None):self.poly([(x,y),(x+w,y+1),(x+w-1,y+h),(x+1,y+h-1)],fill)
 def ellipse(self,x,y,rx,ry,fill=None,start=0,end=math.tau):
  pts=[(x+rx*math.cos(t),y+ry*math.sin(t)) for t in np.linspace(start,end,45)]
  self.line(pts)
  if fill:self.regions.append(([self.point(xx,yy) for xx,yy in pts],fill))
 def arrow(self,x,y,xx,yy):
  self.line([(x,y),(xx,yy)]);aa=math.atan2(yy-y,xx-x)
  self.line([(xx-18*math.cos(aa-.55),yy-18*math.sin(aa-.55)),(xx,yy),(xx-18*math.cos(aa+.55),yy-18*math.sin(aa+.55))])
 def person(self,x,y):
  self.ellipse(x,y,38,42);self.line([(x,y+42),(x,y+140)]);self.line([(x-55,y+100),(x,y+65),(x+55,y+100)]);self.line([(x-45,y+205),(x,y+140),(x+45,y+205)])
  self.ellipse(x-12,y-5,2,3);self.ellipse(x+12,y-5,2,3);self.ellipse(x,y+5,17,14,start=.15,end=2.9)
 def bubble(self,x,y,w,h,fill=None):self.poly([(x,y),(x+w,y),(x+w,y+h),(x+w*.35,y+h),(x+18,y+h+24),(x+25,y+h),(x,y+h)],fill)
 def colorpaths(self):
  result=[]
  # Every colored region is filled by clipped broad marker strokes, not a fade.
  for poly,c in self.regions:
   ys=[p[1] for p in poly]
   for k,y in enumerate(np.arange(min(ys)+5,max(ys)-2,13)):
    xs=[]
    for (x1,y1),(x2,y2) in zip(poly,poly[1:]+poly[:1]):
     if min(y1,y2)<=y<max(y1,y2):xs.append(x1+(y-y1)*(x2-x1)/(y2-y1))
    xs.sort()
    for x1,x2 in zip(xs[::2],xs[1::2]):
     pts=[(x1+2,y),(x2-2,y+.7)]
     if k%2:pts.reverse()
     result.append((pts,c,18))
  return result

def make(name,index):
 b=Icon(540,550 if index%2==0 else 1170,1.05)
 if name in ('book','notebook','dictionary','worksheet','cards'):
  if name=='book':
   b.poly([(-120,-95),(-12,-80),(0,-63),(12,-80),(120,-95),(120,95),(15,110),(0,125),(-15,110),(-120,95)],'#f1dba7');b.line([(0,-63),(0,125)])
   for x in [-95,25]:
    for y in [-35,8,51]:b.line([(x,y),(x+65,y+8)],3)
  elif name=='cards':
   b.box(-95,-95,175,190);b.box(-75,-115,175,190,BLUE);b.box(-55,-135,175,190);b.line([(-25,-75),(70,-75)],4);b.line([(-25,-35),(45,-35)],4)
  else:
   b.box(-105,-130,210,270,GOLD if name=='dictionary' else '#c8dfef');b.line([(-65,-125),(-65,135)],4)
   for y in [-65,-5,55]:
    if name=='worksheet':b.box(-40,y-10,22,22);b.line([(-36,y),( -28,y+8),(-12,y-12)],3);b.line([(0,y),(70,y)],3)
    else:b.line([(-30,y),(65,y)],4)
 elif name in ('bubble','question','reply'):
  b.bubble(-130,-95,260,160,BLUE if name=='bubble' else GREEN)
  if name=='question':b.ellipse(0,-40,25,25,start=3.4,end=7.8);b.line([(0,-15),(0,8)]);b.ellipse(0,35,2,3)
  if name=='reply':b.line([(-65,-15),(-20,30),(70,-55)],7)
 elif name in ('lock','unlock'):
  b.box(-83,-15,166,140,GOLD)
  if name=='lock':b.ellipse(0,-15,56,80,start=math.pi,end=2*math.pi)
  else:b.ellipse(32,-45,56,70,start=math.pi,end=2*math.pi);b.line([(-24,-45),(-24,-15)])
  b.ellipse(0,44,10,12);b.line([(0,55),(0,83)],7)
 elif name in ('person','talk'):
  b.person(0,-70)
  if name=='talk':b.bubble(30,-160,110,65,BLUE)
 elif name=='brain':
  pts=[(-110,25),(-125,-20),(-95,-55),(-100,-95),(-65,-125),(-25,-120),(0,-145),(40,-125),(65,-130),(105,-100),(100,-65),(125,-35),(115,10),(85,35),(55,40),(30,90),(-5,90),(-25,50),(-60,50),(-80,25)]
  b.poly(pts,'#c8dfef');b.line([(-60,-75),(-25,-50),(-45,-5),(0,15),(25,-25),(65,-10)],4)
 elif name=='flow':
  for x,y in [(-110,-100),(15,-10),(-85,85)]:b.box(x,y,95,65,GREEN)
  b.arrow(-10,-50,30,-25);b.arrow(30,65,0,105)
 elif name=='table':
  b.line([(-120,-10),(120,-10)],7);b.line([(-90,-10),(-105,130)]);b.line([(90,-10),(105,130)])
  b.ellipse(0,-20,65,18,BLUE);b.box(-30,-130,60,95,GOLD)
 elif name=='waiter':
  b.person(0,-80);b.line([(-50,15),(-90,-25),(-100,-70)]);b.ellipse(-100,-90,35,10,BLUE)
 elif name=='headphones':
  b.ellipse(0,-10,105,110,start=math.pi,end=math.tau);b.box(-125,-15,50,115,BLUE);b.box(75,-15,50,115,BLUE)
  for x,h in [(-35,45),(0,80),(35,55)]:b.line([(x,10-h/2),(x,10+h/2)],7)
 elif name=='pasta':
  b.ellipse(0,50,130,45,BLUE)
  for k in range(4):b.line([(x,-15+k*13+12*math.sin(x/19+k)) for x in range(-80,81,5)],6,GOLD)
  b.poly([(-12,-30),(0,-67),(30,-65),(24,-35)],GREEN)
 elif name=='calendar':
  b.box(-115,-120,230,245);b.box(-115,-120,230,57,BLUE)
  for x in [-65,65]:b.line([(x,-145),(x,-95)],9)
  for x in [-65,0,65]:
   for y in [-5,65]:b.box(x-14,y-14,28,28,GOLD)
 elif name=='bars':
  b.line([(-125,-140),(-125,125),(130,125)])
  for x,hh in [(-85,65),(-10,130),(65,210)]:b.box(x,125-hh,45,hh,GREEN)
 elif name=='light':
  b.ellipse(0,-55,75,80,GOLD);b.line([(-45,10),(-30,65),(30,65),(45,10)]);b.box(-30,65,60,30)
  for aa in [-2.8,-2,-1.2,-.4]:b.line([(105*math.cos(aa),-55+105*math.sin(aa)),(135*math.cos(aa),-55+135*math.sin(aa))])
 else:b.bubble(-125,-100,250,170,GREEN);b.line([(-65,-20),(65,-20)],5)
 return b
names=['book','notebook','dictionary','bubble','cards','question','brain','lock','lock','unlock','talk','flow','table','waiter','dictionary','headphones','question','person','pasta','reply','calendar','bars','worksheet','cards','bubble','light']
# These paths are authored explicitly; every intended line is traversed completely.
icons=[make(n,i) for i,n in enumerate(names)]

def relocated(icon,cx,cy,scale):
 out=Icon(cx,cy,scale)
 def transform(p):return(cx+(p[0]-icon.cx)/icon.s*scale,cy+(p[1]-icon.cy)/icon.s*scale)
 out.paths=[([transform(p) for p in pts],c,w) for pts,c,w in icon.paths]
 out.regions=[([transform(p) for p in pts],c) for pts,c in icon.regions]
 return out

if v5:
 frames=meta['frames'];frame_starts=[f['start'] for f in frames]
 compositions=[(relocated(make(f['main'],0),430,760,1.65),relocated(make(f['support'],0),760,1130,.95)) for f in frames]

def length(pts):return sum(math.dist(a,z) for a,z in zip(pts,pts[1:]))
def partial(paths,p):
 if p<=0 or not paths:return [],None,INK
 budget=sum(length(q) for q,_,_ in paths)*max(0,min(1,p));result=[];tip=None;color=INK
 for pts,c,w in paths:
  line=[pts[0]]
  for a,z in zip(pts,pts[1:]):
   dist=math.dist(a,z)
   if budget>=dist:line.append(z);budget-=dist
   else:
    if dist:line.append((a[0]+(z[0]-a[0])*budget/dist,a[1]+(z[1]-a[1])*budget/dist))
    budget=0;break
  if len(line)>1:result.append((line,c,w));tip=line[-1];color=c
  if budget<=0:break
 return result,tip,color

def pen(im,tip,c):
 global marker_count
 if tip is None:return
 marker_count+=1
 x,y=tip;d=ImageDraw.Draw(im)
 def pt(a,b):return(x+a*.84-b*.53,y-a*.53-b*.84)
 def polygon(q,c):d.polygon([pt(a,b) for a,b in q],fill=c)
 polygon([(-7,0),(6,0),(10,18),(-9,18)],c)
 polygon([(-9,18),(10,18),(14,40),(-12,40)],'#a7b1ba')
 polygon([(-12,40),(14,40),(14,145),(-12,145)],'#f6f6f1')
 polygon([(-12,52),(14,52),(14,94),(-12,94)],c)
 polygon([(-12,128),(14,128),(14,145),(-12,145)],c)
 d.line([pt(-8,42),pt(-8,126)],fill='#b5bec7',width=2)

def strokes(im,paths,soft=False):
 if soft:
  layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
  for q,c,w in paths:
   c=tuple(int(c[j:j+2],16) for j in (1,3,5)) if c.startswith('#') else (150,180,220)
   d.line(q,fill=c+(115,),width=w,joint='curve')
  im.paste(layer,(0,0),layer)
 else:
  d=ImageDraw.Draw(im)
  for q,c,w in paths:d.line(q,fill=c,width=w,joint='curve')
# Text uses correctly shaped connected Persian glyphs. Its allocated boxes never
# intersect the illustrations: upper icon y=400..770, its labels y=820/920;
# lower icon y=1020..1390, its labels y=1440/1540. Vertical flow suits Reels.
textcache={}
for i,(_,title,sub) in enumerate(beats):
 specs=[('title',title,1460,860,72)] if v5 else [('title',title,820+620*(i%2),820,62 if v4 else 45),('label',sub,920+620*(i%2),800,37 if v4 else 35)]
 for key,text,cy,maxwidth,size in specs:
  rtl=any('\u0600'<=ch<='\u06ff' for ch in text)
  while True:
   selected=font_path(text) if v4 else FA if rtl else EN
   font=ImageFont.truetype(selected,size)
   if font.getlength(text)<=maxwidth:break
   size-=1
  cx=540
  layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
  d.text((cx,cy),text,font=font,anchor='mm',fill=BLUE if key=='title' else INK,direction='rtl' if rtl else 'ltr',stroke_width=1 if v4 and key=='title' else 0)
  mask=np.array(layer.getchannel('A'));contours,_=cv2.findContours(np.uint8(mask>10)*255,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  contours=sorted(contours,key=lambda c:float(c[:,:,0].mean()),reverse=rtl)
  paths=[([tuple(p) for p in c[:,0,:]]+[tuple(c[0,0,:])],BLUE if key=='title' else INK,3) for c in contours]
  textcache[i,key]=(layer,paths)

def write(im,i,key,p):
 layer,paths=textcache[i,key]
 if p>=1-1e-8:im.paste(layer,(0,0),layer);return
 if p<=1e-8:return
 # Marker traces actual glyph contours. Filled glyphs settle behind the tip.
 traced,tip,color=partial(paths,p);mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask)
 for k,(pts,_,_) in enumerate(traced):
  if k<len(traced)-1:md.polygon(pts,fill=255)
  md.line(pts,fill=255,width=8,joint='curve')
 orig=layer.getchannel('A');mask=Image.fromarray(np.minimum(np.array(orig),np.array(mask)))
 im.paste(layer,(0,0),mask);pen(im,tip,color)

def build(t):
 if v5:return build_v5(t)
 global marker_count
 marker_count=0
 page=min(12,int(t//7.2));im=paper.copy()
 for i in [page*2,page*2+1]:
  if i>=len(beats):continue
  age=t-beats[i][0]
  if v4 and i%2:age-=.2  # One marker draws the connector before the lower icon.
  if age<0 or (v4 and age<1e-7):continue
  icon=icons[i]
  # Phase 1 complete outline, phase 2 colored marker hatching, phase 3 lettering.
  outline_end=1.3 if v4 else 1.4
  color_end=1.8 if v4 else 2.05
  outline,tip,col=partial(icon.paths,age/outline_end)
  colored,ctip,ccol=partial(icon.colorpaths(),(age-outline_end)/(color_end-outline_end))
  strokes(im,colored,True);strokes(im,outline)
  if age<outline_end:pen(im,tip,INK)
  elif age<color_end:pen(im,ctip,ccol)
  if v4:
   write(im,i,'title',(age-1.8)/.75)
   write(im,i,'label',(age-2.55)/.5)
  else:
   write(im,i,'title',(age-2.05)/.9)
   write(im,i,'label',(age-2.05)/.9)
 # Connect finished left and right diagram nodes with a deliberate drawn arrow.
 if t>=page*7.2+3.6:
  age=t-(page*7.2+3.6);pts=[(540,962),(540,1010)];head=[(525,990),(540,1010),(555,990)]
  paths=[(pts,INK,4),(head,INK,4)]
  traced,tip,c=partial(paths,age/(.2 if v4 else .42));strokes(im,traced)
  if v4 and age<.2:pen(im,tip,c)
 if v4 and marker_count>1:raise AssertionError(f'Multiple markers at {t}: {marker_count}')
 cue=next((c for c in word_cues if c['start']<=t<c['end']),None)
 if cue:caption(im,cue['text'])
 return im

def build_v5(t):
 global marker_count
 marker_count=0
 index=max(0,min(len(frames)-1,bisect.bisect_right(frame_starts,t)-1))
 frame=frames[index];age=t-frame['start'];main,support=compositions[index]
 im=paper.copy()
 # Each composition grows continuously for 4.35s before its only text arrives.
 main_lines,mtip,_=partial(main.paths,age/1.8)
 main_fill,mctip,mcolor=partial(main.colorpaths(),(age-1.8)/.65)
 support_lines,stip,_=partial(support.paths,(age-2.65)/1.15)
 support_fill,sctip,scolor=partial(support.colorpaths(),(age-3.8)/.55)
 strokes(im,main_fill,True);strokes(im,main_lines)
 strokes(im,support_fill,True);strokes(im,support_lines)
 connector=[([(550,980),(570,1030),(620,1060)],INK,4),([(597,1057),(620,1060),(608,1040)],INK,4)]
 link,ltip,_=partial(connector,(age-2.45)/.2);strokes(im,link)
 if age<1.8:pen(im,mtip,INK)
 elif age<2.45:pen(im,mctip,mcolor)
 elif age<2.65:pen(im,ltip,INK)
 elif age<3.8:pen(im,stip,INK)
 elif age<4.35:pen(im,sctip,scolor)
 write(im,index,'title',(age-4.35)/.9)
 if marker_count>1:raise AssertionError(f'Multiple markers at {t}: {marker_count}')
 cue=next((c for c in word_cues if c['start']<=t<c['end']),None)
 if cue:caption(im,cue['text'])
 return im
if a.style_still is not None:
 im=build(a.style_still)
 if a.sample_word:caption(im,a.sample_word)
 path=P/'previews'/'caption-style-sample.png';im.save(path)
 print(f'{path} (design sample only, not word timing)');raise SystemExit(0)
out=P/'out'/(f'diagram-v{a.revision}-preview.mp4' if a.preview else f'diagram-v{a.revision}.mp4')
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(P/'source.mp3'),'-map','0:v','-map','1:a','-c:v','libx264','-threads','4','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(out)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for f in range(math.ceil(duration*FPS)):
 t=f/FPS;im=build(t);proc.stdin.write(im.tobytes())
 if f in [20,45,68,83,165,475,1380]:im.save(P/'previews'/f'diagram-v{a.revision}-{f}.jpg')
 if f%250==0:print(f'{t:.0f}/{duration:.3f}s',flush=True)
proc.stdin.close()
if proc.wait():raise SystemExit('FFmpeg failed')
if not a.preview:
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=time_base','-of','json',str(out)]))
 tn,td=map(int,meta['streams'][0]['time_base'].split('/'));last=math.ceil(duration*FPS)-1
 lastpts=round(last/FPS*td/tn);samples=len(raw)//2-last*(44100//FPS)
 filt=f'setts=time_base=1/44100:pts=PTS*44100*{tn}/{td}:dts=DTS*44100*{tn}/{td}:duration=if(eq(PTS\\,{lastpts})\\,{samples}\\,{44100//FPS})'
 tmp=out.with_name(out.stem+'-timed.mp4')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-map','0','-c','copy','-bsf:v',filt,'-video_track_timescale','44100','-movflags','+faststart',str(tmp)],check=True);tmp.replace(out)
print(out,flush=True)
