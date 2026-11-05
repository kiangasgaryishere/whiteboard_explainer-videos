from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math,json
P=Path(__file__).parent
INK='#243348'; BLUE='#3469e8'; GREEN='#178a70'; GOLD='#eeac36'; RED='#d75b59'; PAPER='#fcfaf4'
FA='/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
EN='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
class Board:
 def __init__(self,n,label,title):
  self.im=Image.new('RGB',(1080,1920),PAPER); self.d=ImageDraw.Draw(self.im); self.ops=[]
  for x in range(45,1060,38):
   for y in range(55,1860,38): self.d.ellipse((x,y,x+2,y+2),fill='#e4e2da')
  self.text('VOCABULARY / IN ACTION',90,150,28,BLUE)
  self.text(f'{n:02d}',930,150,28,INK)
  self.text(label,540,260,35,GREEN,True)
  self.text(title,540,365,66,INK,True)
 def line(self,pts,c=INK,w=8):
  self.ops.append(('line',pts,c,w)); self.d.line(pts,fill=c,width=w,joint='curve')
 def box(self,x,y,w,h,c=INK):
  self.line([(x+5,y),(x+w,y+3),(x+w-3,y+h),(x,y+h-3),(x+5,y)],c)
 def circle(self,x,y,r,c=INK):
  self.line([(x+r*math.cos(i*math.pi/40),y+r*math.sin(i*math.pi/40)) for i in range(81)],c)
 def arrow(self,x,y,xx,yy,c=BLUE):
  self.line([(x,y),(xx,yy)],c); a=math.atan2(yy-y,xx-x)
  self.line([(xx-25*math.cos(a-.55),yy-25*math.sin(a-.55)),(xx,yy),(xx-25*math.cos(a+.55),yy-25*math.sin(a+.55))],c)
 def text(self,s,x,y,size=45,c=INK,center=False):
  fa=any('\u0600'<=ch<='\u06ff' for ch in s); font=ImageFont.truetype(FA if fa else EN,size)
  self.d.text((x,y),s,font=font,fill=c,anchor='mm' if center else 'lm',direction='rtl' if fa else 'ltr')
 def person(self,x,y,c=INK):
  self.circle(x,y,43,c); self.line([(x,y+45),(x,y+155)],c)
  self.line([(x-70,y+105),(x,y+65),(x+70,y+105)],c)
  self.line([(x-65,y+230),(x,y+155),(x+65,y+230)],c)
 def bubble(self,x,y,w,h,c=BLUE):
  self.line([(x+20,y),(x+w,y+2),(x+w,y+h),(x+70,y+h),(x+30,y+h+35),(x+35,y+h),(x,y+h),(x+2,y),(x+20,y)],c)
 def footer(self,s):
  self.d.rounded_rectangle((90,1480,990,1680),radius=28,fill=INK)
  self.text(s,540,1580,44,'#ffffff',True)
 def save(self,name): self.im.save(P/'previews'/f'{name}.png')
boards=[]
def new(n,label,title):
 b=Board(n,label,title);boards.append(b);return b
b=new(1,'عادت‌های آشنا','لغت جدید یاد می‌گیری؟')
b.box(200,570,680,600);b.line([(280,575),(280,1160)],BLUE)
for y,t in [(700,'معنی فارسی'),(865,'تعریف انگلیسی'),(1030,'مثال دیکشنری')]:
 b.circle(345,y,20,GOLD); b.text(t,620,y,47,INK,True)
b.text('WORD → MEANING',540,1300,42,BLUE,True);b.footer('اما موقع حرف زدن چی؟')
b=new(2,'مشکل کجاست؟','می‌دونی، ولی نمی‌گی!')
b.circle(320,820,150,BLUE);b.text('WORD',320,820,45,BLUE,True); b.arrow(490,820,650,820)
b.person(800,800);b.bubble(640,540,290,150);b.text('…',790,610,75,RED,True)
b.line([(550,760),(610,880)],RED,12);b.line([(610,760),(550,880)],RED,12)
b.text('Passive Vocabulary',540,1200,58,BLUE,True);b.footer('معنی رو می‌فهمی؛ استفاده سخت می‌شه')
b=new(3,'از شناختن به استفاده کردن','لغاتت رو فعال کن')
b.box(125,570,830,260,BLUE);b.text('PASSIVE',540,660,52,BLUE,True);b.text('متوجه می‌شی',540,755,44,INK,True)
b.arrow(540,870,540,1010,GREEN);b.box(125,1050,830,260,GREEN);b.text('ACTIVE',540,1140,60,GREEN,True);b.text('حرف می‌زنی و می‌نویسی',540,1235,44,INK,True);b.footer('Active Vocabulary')
b=new(4,'STEP 01 / CONTEXT','توی یه موقعیت واقعی')
b.person(245,820);b.person(820,760);b.line([(380,1000),(690,1000)],BLUE,12);b.line([(420,1000),(400,1220)]);b.line([(650,1000),(675,1220)])
b.box(470,760,150,200,GOLD);b.text('MENU',545,815,25,INK,True)
b.circle(530,960,56,BLUE);b.text('RECOMMEND',540,1320,65,BLUE,True);b.footer('پیشنهاد دادن')
b=new(5,'STEP 02 / LISTEN','گوش کن؛ توی یک جمله')
b.bubble(150,610,770,350,BLUE);b.text('Can you recommend',535,715,52,INK,True);b.text('a dish?',535,815,66,BLUE,True)
for i,h in enumerate([45,100,155,80,210,120,65,160,95,40]):
 x=280+i*57;b.line([(x,1210-h/2),(x,1210+h/2)],BLUE,12)
b.footer('می‌تونی یه غذا پیشنهاد بدی؟')
b=new(6,'STEP 03 / USE','حالا نوبت توئه')
b.bubble(150,610,770,350,GREEN);b.text("I’d recommend",535,715,59,INK,True);b.text('the pasta.',535,825,68,GREEN,True)
b.circle(540,1160,125,GREEN);b.line([(475,1160),(523,1205),(612,1100)],GREEN,16);b.footer('من پاستا رو پیشنهاد می‌کنم')
b=new(7,'مکالمهٔ واقعی','کلمه رو به کار ببر')
b.bubble(110,590,760,230,BLUE);b.text('Can you recommend',490,660,43,INK,True);b.text('a dish?',490,740,51,BLUE,True)
b.bubble(220,990,760,230,GREEN);b.text("I’d recommend",600,1060,48,INK,True);b.text('the pasta.',600,1140,54,GREEN,True);b.arrow(500,850,600,960,GOLD);b.footer('CONTEXT → LISTEN → USE')
b=new(8,'یادگیری هفتگی','۱۰ لغت کاربردی')
b.box(180,580,720,660,BLUE);b.line([(180,720),(900,720)],BLUE);b.text('WEEKLY',540,655,42,BLUE,True)
for y,t in [(820,'متناسب با سطح زبانت'),(940,'مثال و فایل صوتی'),(1060,'ورک‌شیت تمرین'),(1180,'تمرین اسپیکینگ')]:
 b.line([(245,y),(262,y+18),(295,y-20)],GREEN);b.text(t,590,y,43,INK,True)
b.footer('هر هفته، یک موضوع مشخص')
b=new(9,'بستهٔ هفتگی لغات فعال','آماده‌ای شروع کنی؟')
b.bubble(135,600,810,480,BLUE);b.text('ACTIVE',540,790,118,BLUE,True);b.text('رو کامنت کن',540,975,60,INK,True)
b.arrow(540,1140,540,1330,GREEN);b.footer('بستهٔ هفتگی رو دریافت کن')
b=new(10,'LEARN TO USE THEM','فقط حفظ نکن!')
b.text('MEMORIZE',540,670,70,'#858c96',True);b.line([(240,680),(840,650)],RED,11)
b.text('USE YOUR',540,910,85,BLUE,True);b.text('WORDS.',540,1040,112,GREEN,True);b.line([(255,1150),(830,1150)],GOLD,15);b.footer('یاد بگیر از کلمه‌ها استفاده کنی')
for i,b in enumerate(boards):b.save(f'board-{i+1:02d}')
sheet=Image.new('RGB',(1080,1920),'#d8d5cc')
for i,b in enumerate(boards):
 thumb=b.im.resize((216,384)); sheet.paste(thumb,((i%5)*216,(i//5)*480+350))
sheet.save(P/'previews'/'storyboard.png')
print('10 storyboard boards rendered.')
