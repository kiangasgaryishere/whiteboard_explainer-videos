"""Persistent headings, slightly slower ink and semantic camera direction.
The opening moves from notebook detail to the learner/blocked speech contrast.
"""
import bisect
import math
from PIL import Image, ImageDraw
from direction_v10 import Director as PreviousDirector


class Director(PreviousDirector):
    DRAW_SCALE = 1.08  # 8% longer traversal = about 7.4% lower path speed.

    def scene(self, i):
        if i != 0:
            return super().scene(i)
        learner = self.learner(300, 820, 1.4, True)
        speech = self.prop('question', 725, 625, .92)
        a = self.combine(learner, speech)
        # Establish the expression and speech problem before clothing details.
        a.paths = learner.paths[:16] + speech.paths + learner.paths[16:]
        b = self.combine(self.prop('notebook', 725, 1010, .9),
                         self.prop('cards', 825, 895, .48))
        b.line([(663, 775), (795, 775)], 5, '#c65e50')
        b.paths = b.paths[-1:] + b.paths[:-1]
        return a, b

    @classmethod
    def phase(cls, age):
        return .18 + (age-1.18)*cls.DRAW_SCALE

    def ink(self, surface, icon, age, start, end, approach, active, color=False):
        return super().ink(surface, icon, age, self.phase(start), self.phase(end),
                           approach, active, color)

    def camera(self, surface, index, age):
        # (time, magnification, focus x, focus y). Headings/captions stay in HUD.
        shots = {
            0: [(0,1.32,650,900),(1.05,1.32,650,900),
                (2.25,1.18,465,840),(3.85,1,540,830),(6.9,1,540,830)],
            1: [(0,1.12,390,850),(4.7,1,540,830)],
            2: [(0,1,540,830),(3.8,1.10,430,790),(6.9,1.10,430,790)],
            3: [(0,1.10,500,770),(4.4,1.10,650,890)],
            4: [(0,1.05,330,850),(3.9,1.11,570,810),(6.4,1.11,570,810)],
            5: [(0,1.10,590,750),(4.5,1,540,830)],
            6: [(0,1.05,540,850),(4.5,1,540,830)],
            7: [(0,1,540,830),(2.8,1.09,550,700),(4.8,1.04,540,830)],
            8: [(0,1.04,540,830),(7,1.04,540,830)],
            9: [(0,1.04,540,830),(7,1.04,540,830)],
            10: [(0,1,540,830),(3.9,1.10,470,820),(7.2,1.10,470,820)],
            11: [(0,1.10,640,800),(4.4,1,540,830)],
            12: [(0,1.12,340,830),(4.5,1,540,830)],
        }
        keys = shots[index]
        state = keys[-1][1:]
        for a, b in zip(keys, keys[1:]):
            if age <= b[0]:
                u = max(0,min(1,(age-a[0])/(b[0]-a[0])))
                u = u*u*(3-2*u)
                state = tuple(x+(y-x)*u for x,y in zip(a[1:],b[1:]))
                break
        scale,cx,cy = state
        if abs(scale-1)<1e-8:
            return surface
        np,cv2 = self.g['np'],self.g['cv2']
        # Move the chosen world focus to the artwork viewport center. This is
        # a real pan/reframe, rather than merely zooming about a fixed point.
        matrix = np.array([[scale,0,540-scale*cx],
                           [0,scale,830-scale*cy]],dtype=np.float32)
        strength = float(self.g['meta'].get('camera_motion_strength',1))
        if not 0<=strength<=1:
            raise ValueError('camera_motion_strength must be between 0 and 1')
        identity = np.array([[1,0,0],[0,1,0]],dtype=np.float32)
        matrix = identity + strength*(matrix-identity)
        return Image.fromarray(cv2.warpAffine(np.asarray(surface),matrix,surface.size,
                                              flags=cv2.INTER_CUBIC,
                                              borderMode=cv2.BORDER_CONSTANT))

    def moving_cards(self, art, age):
        if not 1.35 < age < 4.05:
            return
        d = ImageDraw.Draw(art)
        for k,color in enumerate(['#7ca6c8','#e2b962','#75a88c']):
            elapsed = age-k*.10
            if elapsed<1.35:
                continue
            if elapsed < 2.65:
                u = min(1,(elapsed-1.35)/1.3)
                u = u*u*(3-2*u)
            elif elapsed < 3.5:
                u = .97-.065*abs(math.sin((elapsed-2.65)*9))
            else:
                u = max(0,1-(elapsed-3.5)/.35)
            if u<=0:
                continue
            x = 800-70*u+k*7
            y = 920-130*u-k*5
            d.rounded_rectangle((x-18,y-13,x+18,y+13),radius=3,
                                fill=color,outline='#263446',width=2)
            d.line([(x-10,y-3),(x+9,y-3)],fill='#263446',width=2)

    def build(self,t):
        g = self.g
        g['marker_count'] = 0
        index = max(0,min(len(g['frames'])-1,
                          bisect.bisect_right(g['frame_starts'],t)-1))
        frame = g['frames'][index]
        age = t-frame['start']
        im = g['paper'].copy()
        art = Image.new('RGBA',im.size)
        active = []
        a,b = self.scenes[index]
        if 7<=index<=9:
            context = self.contexts[index]
            g['strokes'](art,self.colors[id(context)],True,context.regions)
            g['strokes'](art,context.paths)
        self.ink(art,a,age,3.65,4.55,'top',active,True)
        self.ink(art,b,age,4.05,4.92,'bottom',active,True)
        self.ink(art,a,age,1.18,3.65,'top',active)
        self.ink(art,b,age,1.36,4.05,'bottom',active)
        if index == 0:
            self.moving_cards(art,age)
        if index == 12:
            g['write'](art,index,'bubble-keyword',
                       (age-self.phase(5.02))/(1.05*self.DRAW_SCALE),'bottom')
        for tip,color,approach in active:
            g['pen'](art,tip,color,approach)
        art = self.camera(art,index,age)
        im.paste(art,(0,0),art)
        # A finished heading from the very first frame: no pen call/animation.
        heading,_ = g['textcache'][index,'intro']
        im.paste(heading,(0,0),heading)
        keyword_end = frame['start'] + self.phase(5.02) + 1.05*self.DRAW_SCALE
        # Do not begin a word that would be interrupted/covered by the CTA.
        if index<12 and keyword_end<=g['meta']['cta']['start']:
            g['write'](im,index,'title',
                       (age-self.phase(5.02))/(1.05*self.DRAW_SCALE),'bottom')
        if g['marker_count']>2:
            raise AssertionError(f'Three markers at {t}')
        if t>=g['meta']['cta']['start']:
            g['draw_cta'](im)
        cue = next((c for c in g['word_cues']
                    if c['start']<=t-g['audio_delay']<c['end']),None)
        if cue:
            g['caption'](im,cue['text'],g['subtitle_font'],g['meta']['caption_center_y'],
                         g['meta']['caption_font_size'],g['meta']['caption_half_height'])
        return im
