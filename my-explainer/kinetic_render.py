"""Narrated visual revision: 3.6-second beats, visible markers, incremental type.
Beat timings are editorial placeholders, not verified speech/subtitle alignment.
"""
from pathlib import Path
import argparse,json,math,subprocess
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).parent
W,H,FPS=1080,1920,25
INK='#243348';BLUE='#3065cc';GREEN='#21866b';GOLD='#d99636'
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FA='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
ap=argparse.ArgumentParser();ap.add_argument('--preview',type=float);args=ap.parse_args()
edit=json.loads((P/'kinetic_edit.json').read_text());beats=edit['beats'];scenes=edit['scenes']
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'source.mp3'),'-ar','44100','-ac','1','-f','s16le','-'])
D=len(raw)/88200;duration=min(args.preview,D) if args.preview else D
# Precompute readable, correctly shaped Persian and English text layers.
texts={}
for _,a,b in beats:
 for line,size,y,c in [(a,66,270,BLUE),(b,49,390,INK)]:
  rtl=any('\u0600'<=ch<='\u06ff' for ch in line)
  while True:
   font=ImageFont.truetype(FA if rtl else F,size)
   if font.getlength(line)<=870:break
   size-=1
  layer=Image.new('RGBA',(W,190));d=ImageDraw.Draw(layer)
  d.text((540,95),line,font=font,anchor='mm',direction='rtl' if rtl else 'ltr',fill=c)
  box=layer.getbbox();texts[(line,y)]=(layer,box,rtl)
# Marker geometry: tip is the anchored point, so the pen follows revealed strokes.
def marker(im,x,y,c,angle=-.66,scale=1):
 d=ImageDraw.Draw(im)
 co,si=math.cos(angle),math.sin(angle)
 def pt(a,b):return(x+scale*(a*co-b*si),y+scale*(a*si+b*co))
 def poly(points,fill,outline=None):d.polygon([pt(a,b) for a,b in points],fill=fill)
 # restrained offset shadow, felt nib, metal shoulder, colored barrel + highlight
 poly([(3,3),(10,0),(23,-27),(23,-155),(-10,-155),(-10,-30)],'#e6ded3')
 poly([(-5,1),(6,-2),(12,-21),(-9,-21)],c)
 poly([(-9,-20),(13,-20),(19,-44),(-15,-44)],'#aab4bd')
 poly([(-15,-44),(19,-44),(19,-154),(-15,-154)],'#f8f8f4')
 poly([(-15,-57),(19,-57),(19,-106),(-15,-106)],c)
 poly([(-15,-137),(19,-137),(19,-156),(-15,-156)],c)
 d.line([pt(-10,-45),pt(-10,-134)],fill='#d3d9dc',width=3)
 d.line([pt(14,-46),pt(14,-135)],fill='#8d98a4',width=2)
# Trace a manageable selection of real contours; avoid racing over every pixel.
art={}
for _,_,name in scenes:
 if name in art:continue
 im=Image.open(P/'assets'/f'{name}.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
 arr=np.array(im);gray=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
 bw=np.uint8(gray<100)*255;bw[:470]=0;bw[1500:]=0
 cc,_=cv2.findContours(bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 cc=sorted([cv2.approxPolyDP(c,2,False)[:,0,:] for c in cc if cv2.arcLength(c,False)>95],key=lambda c:float(c[:,1].mean()))
 paths=[];budget=0
 for c in cc:
  length=float(np.linalg.norm(np.diff(c,axis=0),axis=1).sum())
  if budget+length>5200:continue
  paths.append(c);budget+=length
 if not paths:paths=[np.array([[300,800],[750,800]])]
 # Thin horizontal paper strip is part of the generated blank paper, not art.
 # Tile actual paper grain at its native scale; stretching a strip produces streaks.
 patch=im.crop((0,0,W,280));paper=Image.new('RGB',(W,H),'#fff6e8')
 for yy in range(0,H,280):paper.paste(patch,(0,yy))
 art[name]=(im,paper,paths)
# Reveal paths at a measured 900 px/sec, then settle watercolor pigment.
def artframe(name,age,phase):
 source,paper,paths=art[name]
 if age>=5.5:im=source.copy()
 else:
  trace=Image.blend(paper,source,.16);d=ImageDraw.Draw(trace);left=max(0,age-.15)*900;tip=None
  for path in paths:
   points=[tuple(path[0])]
   for a,z in zip(path,path[1:]):
    distance=float(np.linalg.norm(z-a))
    if left>=distance:points.append(tuple(z));left-=distance
    else:
     if distance:points.append(tuple(a+(z-a)*max(0,left)/distance))
     left=0;break
   if len(points)>1:d.line(points,fill=INK,width=4,joint='curve');tip=points[-1]
   if left<=0:break
  wash=max(0,min(1,(age-3.8)/1.7))
  im=Image.blend(trace,source,wash)
  if tip and age<5.5:marker(im,*tip,INK,scale=.9)
 # Small alternating reframing makes every new beat visually distinct.
 zoom=1.0+.012*(phase%3)
 if zoom>1:
  sw,sh=int(W/zoom),int(H/zoom)
  im=im.crop(((W-sw)//2,(H-sh)//2,(W+sw)//2,(H+sh)//2)).resize((W,H),Image.Resampling.BILINEAR)
 return im
# Progressive shaped text reveal plus moving writing marker; Persian flows RTL.
def write(im,line,y,age,start,dur,color):
 layer,box,rtl=texts[(line,y)];x0,y0,x1,y1=box
 p=max(0,min(1,(age-start)/dur))
 if p<=0:return
 if rtl:l=x1-int((x1-x0)*p);r=x1
 else:l=x0;r=x0+int((x1-x0)*p)
 if r>l:im.paste(layer.crop((l,0,r,190)),(l,y-95),layer.crop((l,0,r,190)))
 if 0<p<1:
  x=l if rtl else r
  col=np.array(layer.getchannel('A'))[:,max(0,min(W-1,x))]
  yy=np.where(col>30)[0]
  tipy=y-95+(int(yy[-1]) if len(yy) else 109)
  marker(im,x,tipy,color,angle=-.72 if not rtl else -.45,scale=.8)
name='kinetic-marker-preview.mp4' if args.preview else 'kinetic-marker-v2.mp4'
out=P/'out'/name
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(P/'source.mp3'),'-map','0:v','-map','1:a','-c:v','libx264','-threads','4','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(out)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for frame in range(math.ceil(duration*FPS)):
 t=frame/FPS;i=max(i for i,b in enumerate(beats) if b[0]<=t)
 start,title,sub=beats[i];age=t-start
 s=next((s for s in scenes if s[0]<=t<s[1]),scenes[-1])
 im=artframe(s[2],t-s[0],i)
 write(im,title,270,age,.12,1.38,BLUE)
 write(im,sub,390,age,.90,1.40,INK)
 # Third marker adds a short green underline, a distinct event within each beat.
 if age>2.45:
  p=min(1,(age-2.45)/.65);d=ImageDraw.Draw(im)
  xs=380;xe=xs+320*p
  d.line([(xs,470),(xe,470+3*math.sin(p*math.pi))],fill=GREEN,width=7)
  if p<1:marker(im,xe,470,GREEN,angle=-.5,scale=.8)
 # Add a vocabulary card under the picture for the key restaurant lesson.
 if 50.4<=t<68.4:
  d=ImageDraw.Draw(im);d.rounded_rectangle((180,1510,900,1625),radius=24,fill='#243348')
  word='RECOMMEND';font=ImageFont.truetype(F,47)
  d.text((540,1568),word,font=font,anchor='mm',fill='#f9fbff')
 proc.stdin.write(im.tobytes())
 if frame%250==0:print(f'{t:.0f}/{duration:.3f}s',flush=True)
 if frame in [42,125,412,1375]:im.save(P/'previews'/f'kinetic-check-{frame}.jpg')
proc.stdin.close()
if proc.wait():raise SystemExit('FFmpeg encoding failed')
if not args.preview:
 # Keep the final variable-duration frame aligned to the playable source samples.
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=time_base','-of','json',str(out)]))
 tn,td=map(int,meta['streams'][0]['time_base'].split('/'))
 last=math.ceil(duration*FPS)-1
 lastpts=round(last/FPS*td/tn);lastsamples=len(raw)//2-last*(44100//FPS)
 filt=f'setts=time_base=1/44100:pts=PTS*44100*{tn}/{td}:dts=DTS*44100*{tn}/{td}:duration=if(eq(PTS\\,{lastpts})\\,{lastsamples}\\,{44100//FPS})'
 timed=out.with_name(out.stem+'-timed.mp4')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(out),'-map','0','-c','copy','-bsf:v',filt,'-video_track_timescale','44100','-movflags','+faststart',str(timed)],check=True)
 timed.replace(out)
print(out,flush=True)
