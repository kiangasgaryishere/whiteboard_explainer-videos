"""Authored illustration vocabulary for V9: curved ink, clothed actors, depth,
material details and transcript-specific contextual insets. No raster tracing.
"""
import math

INK='#263446';BLUE='#336cce';GREEN='#23846e';GOLD='#dfaa42';RED='#cf5b55'
SKIN='#ebbf98';HAIR='#775848';PAPER='#f6eedb';PALE='#c9dbe6'

def smooth(points,closed=False,steps=7):
    p=list(points)
    q=([p[-1]]+p+[p[0],p[1]]) if closed else ([p[0]]+p+[p[-1]])
    out=[]
    for i in range(1,len(q)-2):
        a,b,c,d=q[i-1:i+3]
        for j in range(steps):
            t=j/steps
            out.append(tuple(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in (0,1)))
    out.append(p[0] if closed else p[-1]);return out

def curve(b,pts,w=3,c=INK):b.line(smooth(pts),w,c)
def shape(b,pts,fill=None,w=4):
    q=smooth(pts,True);b.poly(q,fill,w)

def hatch(b,x,y,n=5,w=28,step=9):
    for i in range(n):b.line([(x,y+i*step),(x+w,y-7+i*step)],2,'#78818a')

def actor(b,pose='speak',waiter=False):
    # Silhouette, clothing and articulated limbs replace stick figures.
    shape(b,[(-12,-46),(-10,-17),(12,-17),(14,-46)],SKIN)
    shape(b,[(-21,-13),(-53,-3),(-62,36),(-49,102),(45,102),(54,30),(35,-6),(18,-14)],'#e8e8df' if waiter else BLUE)
    shape(b,[(-43,102),(-5,103),(-7,177),(-37,178)],'#667c84' if waiter else '#bac7a1')
    shape(b,[(2,103),(42,102),(35,180),(7,178)],'#667c84' if waiter else '#bac7a1')
    shape(b,[(-39,176),(-49,184),(-53,195),(-1,195),(-5,180)],'#d5d6cc')
    shape(b,[(7,177),(5,194),(55,194),(49,183),(34,179)],'#d5d6cc')
    b.line([(-26,119),(-25,167)],2);b.line([(21,121),(19,168)],2)
    b.line([(-47,189),(-5,189)],2);b.line([(9,188),(49,188)],2)
    # Sleeves and palms: an instructional gesture or a hand touching the chin.
    shape(b,[(-49,1),(-72,25),(-79,58),(-47,75),(-10,62),(-14,48),(-49,51),(-48,25)],SKIN)
    b.line([(-55,35),(-71,32)],3);curve(b,[(-14,49),(-6,53),(-8,59),(-18,62)],2)
    if pose=='think':
        shape(b,[(45,4),(63,17),(80,43),(88,31),(61,-15),(42,-54),(28,-50),(48,-12),(53,24)],SKIN)
        curve(b,[(29,-49),(37,-45),(44,-48)],2)
    else:
        shape(b,[(44,6),(65,15),(88,-2),(99,-18),(107,-15),(101,-4),(118,-6),(119,2),(100,19),(73,37),(47,27)],SKIN)
        b.line([(92,5),(105,2)],2);b.line([(48,15),(63,22)],3)
    # Collar, cuffs, pocket, buttons and cloth folds make the figure feel dressed.
    b.poly([(-20,-12),(-3,4),(-17,14),(-32,-3)],PAPER,3)
    b.poly([(18,-12),(-3,4),(12,16),(33,-3)],PAPER,3)
    b.line([(-3,5),(-2,99)],2)
    for y in [25,50,75]:b.ellipse(3,y,1.8,1.8)
    b.box(16,26,21,23);b.line([(16,29),(37,29)],2)
    curve(b,[(-40,64),(-29,74),(-34,88)],2);b.line([(29,77),(35,91)],2)
    if waiter:
        b.poly([(-30,8),(-7,21),(-14,95),(-45,94)],'#536775',3)
        b.poly([(24,8),(3,21),(7,95),(42,95)],'#536775',3)
        b.poly([(-3,3),(-18,-3),(-17,10)],INK,2);b.poly([(-3,3),(13,-3),(12,10)],INK,2)
    # Asymmetric face, ears, hair locks and eyebrows give the character expression.
    head_start=len(b.paths);head_regions=len(b.regions)
    b.ellipse(-47,-91,10,17,SKIN);b.ellipse(44,-91,8,15,SKIN)
    shape(b,[(-45,-122),(-49,-88),(-30,-49),(0,-41),(32,-56),(44,-96),(31,-132),(-3,-143)],SKIN)
    shape(b,[(-45,-105),(-54,-127),(-37,-142),(-15,-151),(9,-145),(30,-141),(44,-121),(28,-126),(13,-118),(-9,-131),(-25,-116)],HAIR)
    curve(b,[(-42,-129),(-28,-136),(-16,-128)],2)
    b.ellipse(-18,-93,3,5,INK);b.ellipse(15,-94,3,5,INK)
    curve(b,[(-29,-108),(-18,-112),(-8,-109)],3)
    curve(b,[(7,-111),(17,-116 if pose=='think' else -111),(28,-109)],3)
    curve(b,[(0,-91),(-3,-79),(6,-77)],2)
    curve(b,[(-15,-64),(0,-69 if pose=='think' else -57),(17,-64)],3)
    hatch(b,-49,-77,3,9,5)
    # Draw the expressive face first, so the opening never waits for trousers.
    b.paths=b.paths[head_start:]+b.paths[:head_start]
    b.regions=b.regions[head_regions:]+b.regions[:head_regions]
    if waiter:
        b.ellipse(112,28,43,8,PALE);b.box(100,-2,24,25,PAPER)
        curve(b,[(108,-10),(103,-18),(110,-25)],2)

def rich_icon(Icon,name,index=0):
    b=Icon(540,550,1.05)
    if name in ('person','talk','waiter'):
        actor(b,'think' if index in [0,2] and name!='waiter' else 'speak',name=='waiter')
        if name=='talk':
            b.bubble(52,-165,85,55,PALE)
            for x in [72,94,116]:b.ellipse(x,-140,2,2)
    elif name in ('book','notebook','dictionary','worksheet','cards'):
        if name=='book':
            shape(b,[(-125,-95),(-70,-105),(-15,-84),(0,-65),(20,-83),(77,-104),(125,-92),(122,105),(66,100),(17,119),(0,132),(-18,119),(-77,100),(-126,107)],PAPER)
            curve(b,[(0,-65),(-2,30),(0,132)],4)
            curve(b,[(-125,115),(-73,111),(-15,132),(0,140),(18,132),(75,112),(127,114)],3)
            for x in [-103,25]:
                for j,y in enumerate([-40,-2,36,74]):curve(b,[(x,y),(x+35,y-4),(x+72-j*5,y+5)],2)
            hatch(b,-120,90,3,50,6)
        elif name=='cards':
            for dx,dy,c in [(-22,24,PALE),(-10,12,GOLD),(0,0,GREEN)]:
                b.poly([(-100+dx,-115+dy),(95+dx,-125+dy),(108+dx,110+dy),(-90+dx,125+dy)],c)
            b.line([(-58,-61),(65,-66)],3);b.line([(-55,-22),(49,-27)],3)
            b.line([(-45,38),(-13,69),(53,9)],6)
        else:
            b.poly([(-111,-121),(74,-145),(125,-117),(119,129),(-64,151),(-111,125)],BLUE if name=='notebook' else GOLD)
            b.poly([(-97,-111),(72,-132),(110,-109),(105,115),(-65,137),(-97,116)],PAPER)
            b.line([(-79,-111),(-77,120)],3)
            b.poly([(76,-130),(76,-103),(108,-108)],PALE,2)
            for y in [108,116,124]:b.line([(107,y-12),(-60,y+12)],2)
            if name=='notebook':
                for y in range(-100,115,30):b.ellipse(-101,y,12,7)
            for j,y in enumerate([-65,-12,41,88]):
                if name=='worksheet':
                    b.box(-54,y-10,21,21);b.line([(-51,y),(-43,y+8),(-28,y-13)],3)
                    b.line([(-16,y),(67-j*6,y-9)],2)
                else:b.line([(-48,y),(67-j*8,y-13)],3)
            hatch(b,-104,81,4,15,8)
            if name=='worksheet':
                b.poly([(88,128),(115,108),(147,-115),(126,-120)],GOLD,3)
                b.line([(115,108),(88,128),(91,101)],3)
    elif name in ('lock','unlock'):
        b.poly([(-88,-18),(74,-28),(105,-8),(102,133),(-66,149),(-88,127)],GOLD)
        b.line([(74,-28),(74,119),(-66,149)],3);b.line([(74,119),(102,133)],3)
        if name=='lock':
            for r in [48,62]:b.ellipse(-3,-27,r,80,start=math.pi,end=math.tau)
            b.line([(-65,-27),(-65,-15)]);b.line([(59,-27),(59,-20)])
        else:
            for r in [48,62]:b.ellipse(30,-55,r,70,start=math.pi,end=math.tau)
            b.line([(-32,-55),(-32,-17)]);b.line([(92,-55),(92,-73)])
        b.ellipse(-7,42,12,14,INK);b.poly([(-13,55),(-19,90),(4,88),(-1,54)],INK,2)
        hatch(b,78,24,7,16,11)
    elif name=='brain':
        shape(b,[(-116,27),(-132,-19),(-101,-57),(-107,-96),(-72,-125),(-28,-123),(0,-148),(39,-127),(71,-131),(108,-103),(104,-65),(132,-34),(117,13),(86,39),(54,46),(31,99),(-5,96),(-25,53),(-64,56),(-87,29)],PALE)
        for pts in [[(-80,-91),(-57,-100),(-37,-79),(-47,-54),(-27,-41)],[(-92,-22),(-65,-34),(-53,-8),(-70,10)],[(2,-107),(17,-87),(4,-61),(25,-43)],[(66,-97),(52,-67),(77,-51),(93,-58)],[(75,-23),(50,-14),(54,15),(29,26)],[(-25,-17),(-5,-4),(-12,28),(10,45)]]:curve(b,pts,4)
        hatch(b,0,68,3,24,8)
    elif name in ('bubble','question','reply'):
        shape(b,[(-130,-93),(-120,-113),(111,-114),(133,-91),(132,52),(111,76),(-34,79),(-97,117),(-83,77),(-115,77),(-133,57)],GREEN if name=='reply' else BLUE)
        curve(b,[(-116,84),(-101,90),(-92,89)],2)
        if name=='question':
            curve(b,[(-25,-56),(-12,-77),(16,-74),(31,-57),(20,-34),(0,-21),(0,4)],7);b.ellipse(0,33,4,4,INK)
        elif name=='reply':b.line([(-65,-9),(-20,32),(73,-61)],8)
        else:
            for x in [-51,0,51]:b.ellipse(x,-12,4,4,INK)
    elif name=='table':
        b.ellipse(0,-3,139,32,PAPER)
        shape(b,[(-135,-1),(-124,53),(-79,41),(-46,57),(-7,44),(29,57),(73,42),(117,54),(136,-1)],PALE)
        b.line([(-97,49),(-115,146)],5);b.line([(96,49),(113,146)],5)
        b.ellipse(0,-14,69,20);b.ellipse(0,-17,48,12)
        b.poly([(-40,-137),(20,-148),(35,-45),(-30,-34)],GOLD)
        b.line([(-22,-112),(10,-116)],2);b.line([(-19,-88),(12,-92)],2)
        b.ellipse(95,-65,16,24);b.line([(95,-41),(95,-7)]);b.ellipse(95,-5,16,4)
        for x in [-104,-96,-88]:b.line([(x,-50),(x,-15)],2)
        b.line([(-96,-50),(-96,-3)],3);hatch(b,-107,19,4,20,6)
    elif name=='headphones':
        b.poly(smooth([(-112,-5),(-96,-92),(-43,-136),(30,-141),(94,-99),(112,-7),(89,-7),(73,-86),(28,-112),(-33,-109),(-78,-73),(-89,-5)],True),BLUE)
        shape(b,[(-126,-17),(-80,-18),(-77,98),(-122,106)],'#6687b1')
        shape(b,[(80,-18),(124,-17),(123,105),(78,98)],'#6687b1')
        for x in [-110,94]:b.box(x,-2,18,88,PAPER)
        curve(b,[(120,80),(144,126),(103,152),(81,137),(99,122)],3)
        b.line([(99,122),(111,128)],5)
        for x,h in [(-32,37),(0,66),(32,48)]:b.line([(x,27-h/2),(x,27+h/2)],6)
    elif name=='pasta':
        b.ellipse(0,55,136,43,PALE);b.ellipse(0,48,113,30,PAPER)
        for k in range(5):curve(b,[(-86,9+k*12),(-50,-8+k*9),(-8,18+k*10),(39,-6+k*11),(88,14+k*11)],5,GOLD)
        for x,y in [(-54,17),(58,30)]:b.ellipse(x,y,10,8,RED)
        shape(b,[(0,-10),(-13,-42),(7,-53),(21,-22)],GREEN,3)
        shape(b,[(13,-19),(32,-48),(51,-39),(35,-16)],GREEN,3)
        b.line([(-101,-85),(-72,-19)],5)
        for x in [-115,-106,-97,-88]:b.line([(x,-106),(x+12,-80)],2)
        curve(b,[(-81,-54),(-48,-43),(-31,-10),(-48,10)],4,GOLD)
        hatch(b,-89,79,3,45,6)
    elif name=='calendar':
        b.poly([(-120,-118),(106,-125),(121,122),(-106,136)],PAPER)
        b.poly([(-120,-118),(106,-125),(110,-62),(-115,-55)],BLUE)
        for x in [-66,62]:b.ellipse(x,-126,11,22)
        for x in [-66,0,66]:
            for y in [-16,52]:b.box(x-17,y-15,34,30,GOLD)
        b.poly([(-106,124),(121,110),(108,141),(-95,153)],PALE,2)
        hatch(b,88,119,3,17,6)
    elif name=='flow':
        for x,y,c in [(-115,-125,BLUE),(15,-24,GOLD),(-100,85,GREEN)]:b.box(x,y,105,73,c)
        b.arrow(-6,-65,30,-34);b.arrow(33,58,0,113)
        b.ellipse(-62,-88,25,9);b.line([(-82,-80),(-82,-66)],2)
        b.ellipse(67,8,24,23,start=math.pi,end=math.tau);b.line([(43,8),(43,26)],4);b.line([(91,8),(91,26)],4)
        b.bubble(-81,104,65,30,PAPER)
    elif name=='send':
        b.poly([(-121,-90),(130,-8),(-78,120),(-54,18)],BLUE)
        b.line([(-54,18),(130,-8)],3);b.poly([(-54,18),(-78,120),(-19,39)],PALE,2)
        hatch(b,-51,47,4,29,9)
    elif name=='light':
        shape(b,[(-53,10),(-76,-33),(-56,-104),(-2,-131),(55,-106),(76,-45),(49,10),(30,60),(-30,60)],GOLD)
        b.box(-31,61,62,32);b.line([(-30,73),(31,70)],3);b.line([(-26,89),(26,86)],3)
        b.line([(-18,56),(-23,-15),(0,3),(24,-16),(18,56)],3)
        for aa in [-2.8,-2.1,-1.3,-.45]:b.line([(102*math.cos(aa),-48+102*math.sin(aa)),(126*math.cos(aa),-48+126*math.sin(aa))],4)
    else:
        b.bubble(-110,-80,220,145,PALE)
    return b

def context_icon(Icon,index):
    b=Icon(0,0,1)
    if index==0:
        for x,y,c in [(-70,-35,BLUE),(-12,-55,GOLD),(46,-25,GREEN)]:
            b.poly([(x,y),(x+72,y-7),(x+78,y+78),(x+5,y+85)],c)
            b.line([(x+16,y+22),(x+56,y+18)],3);b.line([(x+17,y+42),(x+47,y+38)],3)
    elif index in [1,3]:
        b.poly([(-95,-45),(-10,-37),(0,-23),(12,-37),(95,-45),(94,57),(10,68),(0,79),(-12,68),(-96,57)],PAPER)
        b.line([(0,-23),(0,79)],3)
        for y in [-2,23,48]:b.line([(-75,y),(-24,y+4)],2)
        b.ellipse(57,-20,35,35,PALE);b.line([(80,5),(116,42)],8)
    elif index==2:
        b.ellipse(-45,-15,50,59,GOLD);b.ellipse(-45,-15,38,46)
        b.line([(-45,-48),(-45,-15),(-21,-2)],4)
        b.bubble(30,-40,85,65,PALE);b.line([(61,-22),(61,10)],4);b.ellipse(61,25,2,2)
    elif index==4:
        b.box(-95,-55,140,130,PAPER)
        for y in [-24,1,26,51]:b.line([(-76,y),(11,y)],2)
        b.poly([(36,62),(63,42),(90,-64),(68,-69)],GOLD)
        b.line([(36,62),(41,36)],3);b.line([(65,-56),(86,-51)],3)
    elif index==5:
        for x,y,c in [(-85,25,BLUE),(0,-30,GOLD),(88,25,GREEN)]:b.ellipse(x,y,22,22,c)
        b.arrow(-58,15,-25,-18);b.arrow(26,-18,62,15)
    elif index==6:
        b.box(-106,-38,212,113,PAPER);b.box(-118,-65,236,30,BLUE)
        for x in range(-108,110,36):b.poly([(x,-35),(x+30,-35),(x+25,-5),(x+5,-5)],PALE,2)
        b.box(-65,13,52,62);b.box(24,13,52,62)
    elif index==7:
        b.poly([(-108,-67),(-18,-53),(-8,73),(-96,58)],GOLD)
        b.line([(-91,-36),(-42,-28)],3);b.line([(-89,-9),(-40,-1)],3)
        b.ellipse(58,21,63,23,PALE);b.ellipse(58,15,44,12)
        b.line([(31,-4),(76,2)],4,GOLD)
    elif index==8:
        b.ellipse(-45,-38,31,35,SKIN)
        shape(b,[(-66,0),(-17,0),(-2,64),(-77,65)],BLUE)
        b.bubble(4,-55,109,60,PAPER)
        for x in [30,59,88]:b.ellipse(x,-26,2,2)
    elif index==9:
        b.line([(-70,-64),(-19,65)],7)
        for x in [-89,-78,-67,-56]:b.line([(x,-90),(x+15,-58)],3)
        curve(b,[(-53,-43),(-12,-42),(18,-14),(15,28),(54,42),(92,15)],5,GOLD)
        b.ellipse(47,59,67,16,PALE)
    elif index==10:
        for x,h,c in [(-85,40,BLUE),(-20,75,GOLD),(45,113,GREEN)]:b.box(x,75-h,43,h,c)
        b.arrow(-100,90,112,90)
    elif index==11:
        shape(b,[(-32,-62),(-28,31),(27,31),(32,-62)],BLUE)
        b.ellipse(0,-61,32,21,BLUE);b.ellipse(0,25,51,25,start=0,end=math.pi)
        b.line([(0,51),(0,79)],4);b.line([(-38,80),(38,80)],4)
        for x in [66,92]:curve(b,[(x,-25),(x+15,0),(x,25)],3)
    else:
        b.box(-85,-31,170,106,PALE);b.box(-96,-55,192,34,GOLD)
        b.line([(0,-55),(0,75)],5);b.line([(-85,11),(85,11)],5)
        shape(b,[(0,-55),(-44,-78),(-48,-49),(0,-35),(43,-49),(45,-78)],GREEN,3)
    return b
