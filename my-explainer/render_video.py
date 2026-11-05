"""Render approved boards with animated stroke reveals and verified caption cues.
Requires edit.json: {scenes:[{board,start,end}], captions:[{start,end,text}]}.
Scene starts may precede or follow narration boundaries to implement J/L bridges.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,math
import storyboard as sb
P=Path(__file__).parent
if not (P/'edit.json').exists():
 raise SystemExit('Missing verified edit.json. Obtain alignment.json, match original transcript and verify cue timings before export.')
edit=json.loads((P/'edit.json').read_text())
# Decode to PCM to measure playable samples rather than trusting MP3 padding metadata.
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'source.mp3'),'-f','s16le','-ac','1','-ar','44100','-'])
duration=len(raw)/2/44100
fps=25; count=math.ceil(duration*fps)
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(fps),'-i','-','-i',str(P/'source.mp3'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(P/'out'/'my-explainer.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for frame in range(count):
 t=frame/fps
 scene=next((s for s in edit['scenes'] if s['start']<=t<s['end']),edit['scenes'][-1])
 b=sb.boards[scene['board']-1]; im=b.im.copy();d=ImageDraw.Draw(im)
 # Erase the caption placeholder; the final caption is supplied by verified cues.
 d.rectangle((70,1440,1010,1730),fill=sb.PAPER)
 # Self-drawing outlines: hide each path, then redraw its traveled arc.
 for k,(_,pts,c,w) in enumerate(b.ops):
  d.line(pts,fill=sb.PAPER,width=w+5,joint='curve')
  p=max(0,min(1,(t-scene['start']-.1-k*.075)/.65))
  if p:
   lengths=[math.dist(a,z) for a,z in zip(pts,pts[1:])];remain=sum(lengths)*p;out=[pts[0]]
   for a,z,l in zip(pts,pts[1:],lengths):
    if remain>=l:out.append(z);remain-=l
    else:
     if l:out.append((a[0]+(z[0]-a[0])*remain/l,a[1]+(z[1]-a[1])*remain/l))
     break
   if len(out)>1:d.line(out,fill=c,width=w,joint='curve')
 cue=next((c for c in edit['captions'] if c['start']<=t<c['end']),None)
 if cue:
  text=cue['text'];fa=any('\u0600'<=x<='\u06ff' for x in text);font=ImageFont.truetype(sb.FA if fa else sb.EN,43)
  words=text.split();lines=[];line=''
  for word in words:
   candidate=(line+' '+word).strip()
   if d.textlength(candidate,font=font)>810 and line:lines.append(line);line=word
   else:line=candidate
  if line:lines.append(line)
  if len(lines)>3:raise ValueError('Caption too long; split cue: '+text)
  d.rounded_rectangle((90,1460,990,1690),radius=28,fill=sb.INK)
  for j,line in enumerate(lines):d.text((540,1575+(j-(len(lines)-1)/2)*61),line,font=font,anchor='mm',fill='white' if fa else '#8ab1ff',direction='rtl' if fa else 'ltr')
 proc.stdin.write(im.tobytes())
 if frame%250==0:print(f'{t:.1f}/{duration:.3f}s',flush=True)
proc.stdin.close()
if proc.wait():raise SystemExit('FFmpeg failed')
print('Exported',duration,'seconds; verify container/audio/video endpoints with ffprobe.')
