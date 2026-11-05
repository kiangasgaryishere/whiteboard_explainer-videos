"""Revision 3: complete vector drawings -> marker coloring -> written labels.
No image tracing or raster illustration dissolve. Voice alignment is provisional.
"""
import argparse, math, json, subprocess, bisect
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import numpy as np
import cv2
from caption_style import normalize, font_path, load_cues, caption, group_cues
P=Path(__file__).parent
W,H,FPS=1080,1920,25
INK='#263446'; BLUE='#336cce'; GREEN='#23846e'; GOLD='#dfaa42'; RED='#d7635d'
FA='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'; EN='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
ap=argparse.ArgumentParser();ap.add_argument('--preview',type=float)
ap.add_argument('--revision',type=int,choices=[3,4,5,6,7,8,9,10,11],default=3)
ap.add_argument('--word-captions',type=Path)
ap.add_argument('--style-still',type=float)
ap.add_argument('--sample-word')
ap.add_argument('--allow-estimated-captions',action='store_true',help='Explicitly render unverified draft word timings; not a synchronization claim')
ap.add_argument('--art-sheet',action='store_true')
a=ap.parse_args();v4=a.revision>=4;v5=a.revision>=5;v6=a.revision>=6;v7=a.revision>=7;v8=a.revision>=8;v9=a.revision>=9;v10=a.revision>=10;v11=a.revision==11
headline_font=P/'assets/fonts/Shabnam-Bold.ttf' if v6 else None
subtitle_font=P/'assets/fonts/Shabnam-Medium.ttf' if v6 else None
if a.sample_word and a.style_still is None:ap.error('--sample-word is for a still design sample only')
edit=json.loads((P/'kinetic_edit.json').read_text()); beats=edit['beats']
meta=json.loads((P/f'diagram_v{a.revision}.json').read_text())
if 'short_labels' in meta:
 beats=[[t,title,label] for (t,title,_),label in zip(beats,meta['short_labels'])]
if v5:beats=[[f['start'],f['keyword'],''] for f in meta['frames']]
if v4:beats=[[t,normalize(title),normalize(label)] for t,title,label in beats]
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'source.mp3'),'-ar','44100','-ac','1','-f','s16le','-'])
D=len(raw)/88200
audio_delay=float(meta.get('audio_delay_seconds',0)) if v7 else 0
output_samples=len(raw)//2+round(audio_delay*44100)
output_duration=output_samples/44100
duration=min(a.preview,output_duration) if a.preview else output_duration
word_cues=load_cues(a.word_captions,P/'source.mp3',D,a.allow_estimated_captions) if a.word_captions else []
if v7:word_cues=group_cues(word_cues,meta['caption_group_words'])
if a.allow_estimated_captions:print('DRAFT caption timing enabled: not verified speech alignment.',flush=True)
# Soft stationery grain: no stretched strips, decorative headers or slide numbers.
rng=np.random.default_rng(47);noise=rng.normal(0,.65,(H,W,1))
paper=Image.fromarray(np.uint8(np.clip(np.array([253,250,242])[None,None,:]+noise,0,255)))
if v4:paper=Image.open(P/'assets'/'notebook-paper.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
if v10:paper=Image.open(P/meta['background']).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
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
 elif name=='send':
  b.poly([(-115,-90),(125,-10),(-75,115),(-55,15)],BLUE)
  b.line([(-55,15),(125,-10)])
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
 compositions=[(relocated(make(f['main'],0),430,760,1.65),relocated(make(f['support'],0),760,(1020 if i==len(frames)-1 else 1080) if v7 else 1130,.95)) for i,f in enumerate(frames)]

if v9:
 from art_direction import rich_icon, context_icon
 def bounds(icon):
  pts=[p for path,_,_ in icon.paths for p in path]
  return min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)
 def area(icon):
  x,y,xx,yy=bounds(icon);return (xx-x)*(yy-y)
 previous_compositions=compositions;compositions=[];contexts9=[];plain9=[];art_metrics=[]
 for i,f in enumerate(frames):
  primary=relocated(rich_icon(Icon,f['main'],i),370 if i==0 else 400,850 if i==0 else 760,1.65)
  secondary=relocated(rich_icon(Icon,f['support'],i),790 if i==0 else 760,1110 if i==0 else (930 if i>=11 else 980),.95)
  base=context_icon(Icon,i);x,y,xx,yy=bounds(base);cw,ch=xx-x,yy-y
  original_area=sum(area(b) for b in previous_compositions[i]);target=original_area*.30
  scale=min(math.sqrt(target/(cw*ch)),380/cw,240/ch)
  context=relocated(base,740,350,scale);contexts9.append(context)
  plain=Icon(primary.cx,primary.cy,primary.s);plain.paths=list(primary.paths);plain.regions=list(primary.regions);plain9.append(plain)
  _,top,_,bottom=bounds(primary);primary.split_cut=(top+bottom)/2
  primary.paths+=context.paths;primary.regions+=context.regions
  compositions.append((primary,secondary))
  art_metrics.append({'frame':i+1,'retained_concepts':[f['main'],f['support']],'context_inset_bbox_area_ratio':round(area(context)/original_area,3),'target':.30})
 (P/'previews'/'diagram-v9-art-metrics.json').write_text(json.dumps(art_metrics,indent=2))
 # World-coordinate hook graphics: speech becomes visibly blocked, without SFX.
 hook_speech=Icon(0,0,1);hook_speech.bubble(575,600,335,160,BLUE)
 for x in [660,720,780]:hook_speech.ellipse(x,675,4,4)
 hook_block=Icon(0,0,1);hook_block.box(522,692,52,54,RED)
 hook_block.ellipse(548,692,18,22,start=math.pi,end=math.tau)
 hook_block.line([(514,682),(581,754)],8,RED);hook_block.line([(581,682),(514,754)],8,RED)
 hook_link=[([(465,735),(518,718)],INK,5)]

def split_paths(paths, y):
 upper=[];lower=[]
 for pts,c,w in paths:
  for a,z in zip(pts,pts[1:]):
   if (a[1]<y<z[1]) or (z[1]<y<a[1]):
    q=(a[0]+(z[0]-a[0])*(y-a[1])/(z[1]-a[1]),y)
    (upper if a[1]<=y else lower).append(([a,q],c,w))
    (upper if z[1]<=y else lower).append(([q,z],c,w))
   else:(upper if (a[1]+z[1])/2<=y else lower).append(([a,z],c,w))
 return upper,lower

if v8:
 split_art=[]
 for main,support in compositions:
  ys=[p[1] for pts,_,_ in main.paths for p in pts];cut=getattr(main,'split_cut',(min(ys)+max(ys))/2)
  split_art.append((split_paths(main.paths,cut),split_paths(main.colorpaths(),cut)))

def length(pts):return sum(math.dist(a,z) for a,z in zip(pts,pts[1:]))
if v8:
 for (main,_),((upper,lower),_) in zip(compositions,split_art):
  original=sum(length(pts) for pts,_,_ in main.paths)
  divided=sum(length(pts) for pts,_,_ in upper+lower)
  assert abs(original-divided)<1e-6, 'Split figure lost or duplicated a stroke'
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

def pen(im,tip,c,approach=None):
 global marker_count
 if tip is None:return
 marker_count+=1
 x,y=tip;d=ImageDraw.Draw(im)
 lower=v7 and approach=='bottom'
 def pt(a,b):
  if lower:return(x+(a*.84+b*.53)*.78,y+(-a*.53+b*.84)*.78)
  return(x+a*.84-b*.53,y-a*.53-b*.84)
 def polygon(q,c):d.polygon([pt(a,b) for a,b in q],fill=c)
 if v10:
  hull=[pt(a,b) for a,b in [(-12,0),(14,0),(16,166),(-14,166)]]
  x0=int(min(p[0] for p in hull))-20;y0=int(min(p[1] for p in hull))-20
  shadow=Image.new('RGBA',(220,230));sd=ImageDraw.Draw(shadow)
  sd.polygon([(xx-x0+13,yy-y0+13) for xx,yy in hull],fill=(55,43,30,65))
  shadow=shadow.filter(ImageFilter.GaussianBlur(7));im.paste(shadow,(x0,y0),shadow)
 polygon([(-7,0),(6,0),(10,18),(-9,18)],c)
 polygon([(-9,18),(10,18),(14,40),(-12,40)],'#a7b1ba')
 polygon([(-12,40),(14,40),(14,145),(-12,145)],'#fff0d0' if lower else '#f6f6f1')
 polygon([(-12,52),(14,52),(14,94),(-12,94)],c)
 polygon([(-12,128),(14,128),(14,145),(-12,145)],c)
 d.line([pt(-8,42),pt(-8,126)],fill='#b5bec7',width=2)
 if lower:d.line([pt(-11,111),pt(13,111)],fill='#243348',width=3)
 if v10:
  d.line([pt(-7,44),pt(-7,140)],fill='#ffffff',width=4)
  d.line([pt(11,43),pt(11,141)],fill='#979c9a',width=3)

paint_masks={}
def strokes(im,paths,soft=False,clip=None):
 if soft:
  layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer)
  for q,c,w in paths:
   c=tuple(int(c[j:j+2],16) for j in (1,3,5)) if c.startswith('#') else (150,180,220)
   d.line(q,fill=c+(115,),width=w,joint='curve')
  if clip:
   key=id(clip)
   if key not in paint_masks:
    mask=Image.new('L',im.size);md=ImageDraw.Draw(mask)
    for polygon,_ in clip:md.polygon(polygon,fill=255)
    paint_masks[key]=mask
   layer.putalpha(ImageChops.multiply(layer.getchannel('A'),paint_masks[key]))
  if im.mode=='RGBA':im.alpha_composite(layer)
  else:im.paste(layer,(0,0),layer)
 else:
  d=ImageDraw.Draw(im)
  for q,c,w in paths:d.line(q,fill=c,width=w,joint='curve')
# Text uses correctly shaped connected Persian glyphs. Its allocated boxes never
# intersect the illustrations: upper icon y=400..770, its labels y=820/920;
# lower icon y=1020..1390, its labels y=1440/1540. Vertical flow suits Reels.
textcache={}
for i,(_,title,sub) in enumerate(beats):
 specs=[('title',title,1340 if v7 else 1460,860,72)] if v5 else [('title',title,820+620*(i%2),820,62 if v4 else 45),('label',sub,920+620*(i%2),800,37 if v4 else 35)]
 if v10:specs.append(('intro',meta['frames'][i]['intro'],270,900,74))
 for key,text,cy,maxwidth,size in specs:
  rtl=any('\u0600'<=ch<='\u06ff' for ch in text)
  while True:
   selected=font_path(text,headline_font if rtl else None) if v4 else FA if rtl else EN
   font=ImageFont.truetype(selected,size)
   if font.getlength(text)<=maxwidth:break
   size-=1
  cx=540
  layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
  d.text((cx,cy),text,font=font,anchor='mm',fill=('#151515' if v11 and key=='intro' else BLUE if key=='title' else INK),direction='rtl' if rtl else 'ltr',stroke_width=1 if v4 and key=='title' else 0)
  mask=np.array(layer.getchannel('A'));contours,_=cv2.findContours(np.uint8(mask>10)*255,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  contours=sorted(contours,key=lambda c:float(c[:,:,0].mean()),reverse=rtl)
  paths=[([tuple(p) for p in c[:,0,:]]+[tuple(c[0,0,:])],BLUE if key=='title' else INK,3) for c in contours]
  textcache[i,key]=(layer,paths)

def write(im,i,key,p,approach=None):
 layer,paths=textcache[i,key]
 if p>=1-1e-8:im.paste(layer,(0,0),layer);return
 if p<=1e-8:return
 # Marker traces actual glyph contours. Filled glyphs settle behind the tip.
 traced,tip,color=partial(paths,p);mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask)
 for k,(pts,_,_) in enumerate(traced):
  if k<len(traced)-1:md.polygon(pts,fill=255)
  md.line(pts,fill=255,width=8,joint='curve')
 orig=layer.getchannel('A');mask=Image.fromarray(np.minimum(np.array(orig),np.array(mask)))
 im.paste(layer,(0,0),mask);pen(im,tip,color,approach)

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
 if v8:return build_v8(t)
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
 if age<1.8:pen(im,mtip,INK,'top')
 elif age<2.45:pen(im,mctip,mcolor,'bottom')
 elif age<2.65:pen(im,ltip,INK,'top')
 elif age<3.8:pen(im,stip,INK,'bottom')
 elif age<4.35:pen(im,sctip,scolor,'bottom')
 if not v6 or t<meta['cta']['start']:write(im,index,'title',(age-4.35)/.9,'top' if index%2==0 else 'bottom')
 if marker_count>1:raise AssertionError(f'Multiple markers at {t}: {marker_count}')
 if v6:
  if index==len(frames)-1 and age>=2.45:
   d=ImageDraw.Draw(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',74)
   d.text((430,730),'ACTIVE',font=f,anchor='mm',fill=INK)
  if t>=meta['cta']['start']:draw_cta(im)
 cue_time=t-audio_delay
 cue=next((c for c in word_cues if c['start']<=cue_time<c['end']),None)
 if cue:caption(im,cue['text'],subtitle_font,meta['caption_center_y'] if v7 else 1735)
 return im

def build_v8(t):
 if v10:return director10.build(t)
 if v9:return build_v9(t)
 global marker_count
 marker_count=0
 index=max(0,min(len(frames)-1,bisect.bisect_right(frame_starts,t)-1))
 frame=frames[index];age=t-frame['start'];main,support=compositions[index]
 im=paper.copy();active=[]
 connector=[([(550,980),(570,1030),(620,1060)],INK,4),([(597,1057),(620,1060),(608,1040)],INK,4)]
 def task(paths,start,end,approach,soft=False,clip=None):
  traced,tip,color=partial(paths,(age-start)/(end-start));strokes(im,traced,soft,clip)
  if start<=age<end and tip is not None:active.append((tip,color,approach))
 if frame['draw_mode']=='split-primary':
  (upper,lower),(upper_color,lower_color)=split_art[index]
  # Each marker owns a spatially separate half of the same drawing.
  task(upper_color,2.1,2.95,'top',True);task(lower_color,2.1,2.95,'bottom',True)
  task(upper,0,2.0,'top');task(lower,.15,2.1,'bottom')
  task(support.colorpaths(),4.05,4.75,'bottom',True)
  task(support.paths,2.95,4.05,'bottom')
  task(connector,3.0,3.3,'top');text_start=3.3
 else:
  # Upper marker builds the main picture while the lower builds its companion.
  task(main.colorpaths(),2.0,2.8,'top',True);task(main.paths,0,2.0,'top')
  task(support.colorpaths(),3.45,4.5,'bottom',True);task(support.paths,.25,3.45,'bottom')
  task(connector,2.8,3.15,'top');text_start=3.15
 for tip,color,approach in active:pen(im,tip,color,approach)
 if t<meta['cta']['start']:
  # Upper marker writes while the lower marker is still drawing/coloring below.
  write(im,index,'title',(age-text_start)/1.2,'top')
  if index%3==1:
   task_line=[([(380,1405),(700,1405)],GREEN,5)]
   traced,tip,c=partial(task_line,(age-5.15)/.5);strokes(im,traced)
   if 5.15<=age<5.65:pen(im,tip,c,'top')
 if index%2==0:
  x,y=support.cx+145*support.s,support.cy-80*support.s
  rays=[([(x,y),(x+20,y-10)],GOLD,4),([(x+5,y+20),(x+28,y+22)],GOLD,4)]
  traced,tip,c=partial(rays,(age-5.15)/.6);strokes(im,traced)
  if 5.15<=age<5.75:pen(im,tip,c,'bottom')
 if marker_count>2:raise AssertionError(f'More than two markers at {t}: {marker_count}')
 if index==len(frames)-1 and age>=2.8:
  d=ImageDraw.Draw(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',74)
  d.text((430,730),'ACTIVE',font=f,anchor='mm',fill=INK)
 if t>=meta['cta']['start']:draw_cta(im)
 cue=next((c for c in word_cues if c['start']<=t-audio_delay<c['end']),None)
 if cue:caption(im,cue['text'],subtitle_font,meta['caption_center_y'],meta['caption_font_size'],meta['caption_half_height'])
 return im

def finish_v9(im,t,active):
 for tip,color,approach in active:pen(im,tip,color,approach)
 if marker_count>2:raise AssertionError(f'More than two markers at {t}: {marker_count}')
 if t>=meta['cta']['start']:draw_cta(im)
 cue=next((c for c in word_cues if c['start']<=t-audio_delay<c['end']),None)
 if cue:caption(im,cue['text'],subtitle_font,meta['caption_center_y'],meta['caption_font_size'],meta['caption_half_height'])
 return im

def build_v9(t):
 global marker_count
 marker_count=0
 index=max(0,min(len(frames)-1,bisect.bisect_right(frame_starts,t)-1))
 if index==0:return hook_v9(t)
 frame=frames[index];age=t-frame['start'];main,support=compositions[index]
 im=paper.copy();active=[]
 def task(paths,start,end,approach,soft=False,clip=None):
  traced,tip,color=partial(paths,(age-start)/(end-start));strokes(im,traced,soft,clip)
  if start<=age<end and tip is not None:active.append((tip,color,approach))
 connector=[([(530,1000),(565,1030),(620,1040)],INK,4),([(599,1024),(620,1040),(596,1046)],INK,4)]
 if frame['draw_mode']=='split-primary':
  (upper,lower),(uc,lc)=split_art[index]
  task(uc,2.8,3.65,'top',True,main.regions);task(lc,2.8,3.65,'bottom',True,main.regions)
  task(upper,0,2.7,'top');task(lower,.15,2.8,'bottom')
  task(support.colorpaths(),4.75,5.4,'bottom',True,support.regions);task(support.paths,3.65,4.75,'bottom')
  task(connector,3.65,3.95,'top');text_start=3.95
 else:
  task(main.colorpaths(),2.65,3.55,'top',True,main.regions);task(main.paths,0,2.65,'top')
  task(support.colorpaths(),4.0,5.2,'bottom',True,support.regions);task(support.paths,.2,4.0,'bottom')
  task(connector,3.55,3.85,'top');text_start=3.85
 if t<meta['cta']['start']:
  write(im,index,'title',(age-text_start)/1.15,'top')
  if index%3==1:
   lines=[([(380,1405),(700,1405)],GREEN,4)]
   task(lines,5.35,5.85,'top')
 if index%2==0:
  rays=[([(920,1020),(945,1007)],GOLD,4),([(926,1040),(952,1047)],GOLD,4)]
  task(rays,5.4,5.95,'bottom')
 if index==len(frames)-1 and age>=3.55:
  d=ImageDraw.Draw(im);f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',74)
  d.text((main.cx,main.cy-25),'ACTIVE',font=f,anchor='mm',fill=INK)
 return finish_v9(im,t,active)

def hook_v9(t):
 global marker_count
 marker_count=0;im=paper.copy();active=[];main=plain9[0];support=compositions[0][1];context=contexts9[0]
 def task(paths,start,end,approach,soft=False,clip=None):
  traced,tip,c=partial(paths,(t-start)/(end-start));strokes(im,traced,soft,clip)
  if start<=t<end and tip is not None:active.append((tip,c,approach))
 task(main.colorpaths(),1.65,2.2,'top',True,main.regions);task(main.paths,0,1.65,'top')
 task(context.colorpaths(),1.35,1.9,'bottom',True,context.regions);task(context.paths,.08,1.35,'bottom')
 task(hook_speech.colorpaths(),2.85,3.05,'top',True,hook_speech.regions);task(hook_speech.paths,2.2,2.85,'top')
 task(hook_link,1.9,2.2,'bottom');task(hook_block.colorpaths(),2.85,3.1,'bottom',True,hook_block.regions);task(hook_block.paths,2.2,2.85,'bottom')
 task(support.colorpaths(),4.75,5.4,'bottom',True,support.regions);task(support.paths,3.15,4.75,'bottom')
 # Word cards travel towards speech, hit the blockage and recoil: a visual hook,
 # not an invented number/claim or a change to the narrator's supplied words.
 if 1.15<t<3.25:
  d=ImageDraw.Draw(im)
  for k in range(3):
   u=max(0,min(.91,(t-1.15-k*.15)/1.05))
   if u<=0:continue
   if t>2.25:u=max(0,u-.09*abs(math.sin((t-2.25)*8)))
   x=730-180*u;y=450+250*u
   d.rounded_rectangle((x-15,y-12,x+15,y+12),radius=3,fill=['#729dcc','#e3b85d','#77a58e'][k],outline=INK,width=2)
   d.line([(x-8,y-3),(x+8,y-3)],fill=INK,width=2)
 write(im,0,'title',(t-3.1)/.85,'top')
 return finish_v9(im,t,active)

def draw_cta(im):
 d=ImageDraw.Draw(im)
 if v7:
  d.rounded_rectangle((110,1250,970,1450),radius=28,fill='#20334c',outline='#e3b85d',width=3)
  f=ImageFont.truetype(str(headline_font),72)
  d.text((540,1315),'کلمهٔ ACTIVE',font=f,anchor='mm',direction='rtl',fill='#f1c96f')
  f=ImageFont.truetype(str(headline_font),54)
  d.text((540,1400),'را کامنت کن',font=f,anchor='mm',direction='rtl',fill='#ffffff')
  return
 d.rounded_rectangle((130,1330,950,1620),radius=30,fill='#20334c',outline='#e3b85d',width=3)
 # Three deliberate text runs keep English spelling and Persian order unambiguous.
 f=ImageFont.truetype(str(headline_font),44)
 d.text((540,1374),'کلمهٔ',font=f,anchor='mm',direction='rtl',fill='#ffffff')
 en=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',92)
 d.text((540,1467),'ACTIVE',font=en,anchor='mm',fill='#f1c96f')
 f=ImageFont.truetype(str(headline_font),58)
 d.text((540,1562),'را کامنت کن',font=f,anchor='mm',direction='rtl',fill='#ffffff')
if v10:
 if v11:
  from direction_v11 import Director
 else:
  from direction_v10 import Director
 director10=Director(globals())
if a.style_still is not None:
 im=build(a.style_still)
 if a.sample_word:caption(im,a.sample_word,subtitle_font,meta['caption_center_y'] if v7 else 1735)
 path=P/'previews'/(f'diagram-v{a.revision}-style.png' if v6 else 'caption-style-sample.png');im.save(path)
 print(f'{path} (design sample only, not word timing)');raise SystemExit(0)
if a.art_sheet:
 sheet=Image.new('RGB',(1080,1920),'#e2e5e6')
 for i,f in enumerate(frames):
  im=build(f['end']-.35);im.save(P/'previews'/f'diagram-v{a.revision}-art-{i+1:02d}.png')
  sheet.paste(im.resize((270,480)),((i%4)*270,(i//4)*480))
 sheet.save(P/'previews'/f'diagram-v{a.revision}-art-sheet.png');print('Art sheet saved.');raise SystemExit(0)
out=P/'out'/(f'diagram-v{a.revision}-preview.mp4' if a.preview else f'diagram-v{a.revision}.mp4')
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(P/'source.mp3'),'-map','0:v','-map','1:a','-c:v','libx264','-threads','4','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(out)]
if audio_delay:cmd=cmd[:-1]+['-af',f'adelay={round(audio_delay*1000)}:all=1']+cmd[-1:]
if v8:cmd=cmd[:-1]+['-bf','0']+cmd[-1:]  # Exact final-picture hold without B-frame reordering.
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
marker_activity={0:0,1:0,2:0}
for f in range(math.ceil(duration*FPS)):
 t=f/FPS;im=build(t);proc.stdin.write(im.tobytes())
 if v8:marker_activity[marker_count]+=1
 if f in [20,45,68,83,165,475,1380]:im.save(P/'previews'/f'diagram-v{a.revision}-{f}.jpg')
 if f%250==0:print(f'{t:.0f}/{duration:.3f}s',flush=True)
proc.stdin.close()
if proc.wait():raise SystemExit('FFmpeg failed')
if not a.preview:
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=time_base,nb_frames','-of','json',str(out)]))
 # FFmpeg can round -t down to a frame; use the actual encoded picture count.
 tn,td=map(int,meta['streams'][0]['time_base'].split('/'));last=int(meta['streams'][0]['nb_frames'])-1
 lastpts=round(last/FPS*td/tn);samples=output_samples-last*(44100//FPS)
 filt=f'setts=time_base=1/44100:pts=PTS*44100*{tn}/{td}:dts=DTS*44100*{tn}/{td}:duration=if(eq(PTS\\,{lastpts})\\,{samples}\\,{44100//FPS})'
 tmp=out.with_name(out.stem+'-timed.mp4')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-map','0','-c','copy','-bsf:v',filt,'-video_track_timescale','44100','-movflags','+faststart',str(tmp)],check=True);tmp.replace(out)
if v8:
 (P/'previews'/f'diagram-v{a.revision}-marker-activity{"-preview" if a.preview else ""}.json').write_text(json.dumps({'total_frames':sum(marker_activity.values()),'count_basis':'rendered frames before mux rounding','encoded_frames':None if a.preview else int(meta['streams'][0]['nb_frames']),'frames_by_visible_marker_count':marker_activity},indent=2))
 print('Marker activity:',marker_activity,flush=True)
if v7 and word_cues and not a.preview:
 source=json.loads(a.word_captions.read_text())
 shifted=[dict(c,start=round(c['start']+audio_delay,6),end=round(c['end']+audio_delay,6)) for c in word_cues]
 suffix='estimated' if source.get('reviewed') is not True else 'reviewed'
 base=P/f'captions-v{a.revision}.{suffix}'
 base.with_suffix(base.suffix+'.json').write_text(json.dumps({'reviewed':source.get('reviewed',False),'timing_status':source.get('timing_status','reviewed'),'source_sha256':source['source_sha256'],'audio_delay_seconds':audio_delay,'groups':shifted},ensure_ascii=False,indent=2))
 def stamp(t):
  ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 base.with_suffix(base.suffix+'.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(shifted))+'\n')
print(out,flush=True)
