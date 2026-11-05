"""Text-led direction: a recurring adult learner, continuing restaurant scene,
two complementary pens, shaded stationery and restrained camera reframing.
All new drawings follow the opening headline; keywords follow the picture.
"""
import bisect
import math
from PIL import Image, ImageDraw
from art_direction import actor, rich_icon, context_icon, curve


class Director:
    def __init__(self, g):
        self.g = g
        self.Icon = g['Icon']
        self.scenes = [self.scene(i) for i in range(len(g['frames']))]
        self.contexts = {i: self.restaurant(i) for i in [7, 8, 9]}
        self.colors = {id(icon): icon.colorpaths()
                       for pair in self.scenes for icon in pair}
        self.colors.update({id(icon): icon.colorpaths() for icon in self.contexts.values()})
        layer, paths = g['textcache'][12, 'title']
        bubble_layer = Image.new('RGBA', layer.size)
        bubble_layer.paste(layer, (195, -665))
        g['textcache'][12, 'bubble-keyword'] = (
            bubble_layer,
            [([(x+195, y-665) for x, y in pts], c, w) for pts, c, w in paths],
        )

    def empty(self):
        return self.Icon(0, 0, 1)

    def combine(self, *icons):
        out = self.empty()
        for icon in icons:
            out.paths += icon.paths
            out.regions += icon.regions
        return out

    def prop(self, name, x, y, scale=1, index=0):
        return self.g['relocated'](rich_icon(self.Icon, name, index), x, y, scale)

    def learner(self, x, y, scale=1, thoughtful=False, waiter=False):
        icon = self.empty()
        actor(icon, 'think' if thoughtful else 'speak', waiter)
        if waiter:
            icon.ellipse(-18, -93, 10, 9)
            icon.ellipse(15, -94, 10, 9)
            icon.line([(-8, -94), (5, -94)], 2)
            curve(icon, [(-15, -70), (-6, -74), (0, -71), (7, -74), (16, -70)], 4, '#604b3d')
        # Less oversized head and longer lower body: adult editorial proportions.
        def adult(p):
            xx, yy = p
            if yy < -41:
                return xx * .86, -85 + (yy + 85) * .82
            return xx, yy * 1.18 if yy > 0 else yy
        icon.paths = [([adult(p) for p in pts], c, w) for pts, c, w in icon.paths]
        icon.regions = [([adult(p) for p in pts], c) for pts, c in icon.regions]
        return self.g['relocated'](icon, x, y, scale)

    def restaurant(self, index):
        return self.combine(
            self.learner(240, 855, 1.12, thoughtful=index < 9),
            self.prop('table', 565, 960, 1.05),
            self.learner(850, 850, 1.05, waiter=True),
        )

    def scene(self, i):
        Z = self.empty
        if i == 0:
            a = self.combine(self.learner(300, 820, 1.4, True), self.prop('notebook', 725, 1010, .9))
            b = self.combine(self.prop('question', 725, 625, .92), self.prop('cards', 825, 895, .48))
        elif i == 1:
            a = self.combine(self.prop('dictionary', 350, 780, 1.3), self.prop('notebook', 410, 1100, .55))
            b = self.combine(self.learner(805, 860, 1.05, True), self.prop('book', 600, 1120, .45))
        elif i == 2:
            a = self.learner(315, 840, 1.5, True)
            b = self.combine(self.prop('question', 745, 650, 1), self.prop('lock', 740, 1010, .65))
        elif i == 3:
            a = self.combine(self.prop('brain', 580, 705, 1.25), self.learner(280, 970, .9, True))
            b = self.combine(self.prop('lock', 825, 995, .72), self.prop('book', 400, 1160, .4))
        elif i == 4:
            a = self.learner(640, 825, 1.4)
            b = self.combine(self.prop('unlock', 285, 800, 1.1), self.prop('reply', 825, 595, .65))
        elif i == 5:
            a = self.prop('flow', 590, 775, 1.65)
            b = self.combine(self.learner(235, 940, .95), self.prop('light', 820, 1110, .47))
        elif i == 6:
            a = self.combine(self.learner(240, 855, 1.12, True), self.prop('table', 565, 960, 1.05))
            b = self.combine(self.learner(850, 850, 1.05, waiter=True), self.prop('question', 540, 555, .7))
        elif i == 7:
            a = self.prop('headphones', 550, 545, .78)
            b = Z()
            for radius in [46, 70, 94]:
                b.ellipse(680, 540, radius, radius*.72, start=-.65, end=.65)
        elif i == 8:
            a = self.prop('question', 555, 520, .82)
            b = Z()
            b.arrow(365, 765, 465, 630)
        elif i == 9:
            a = self.prop('reply', 555, 520, .82)
            b = self.prop('pasta', 565, 920, .8)
        elif i == 10:
            a = self.combine(self.prop('calendar', 370, 780, 1.3), self.learner(770, 865, .95))
            b = self.prop('cards', 530, 1110, .65)
        elif i == 11:
            a = self.combine(self.learner(265, 860, 1.12), self.prop('worksheet', 660, 800, 1.2))
            b = self.prop('headphones', 865, 1120, .47)
        else:
            a = self.combine(self.learner(275, 875, 1.15), self.prop('bubble', 735, 690, 1.1))
            b = self.combine(self.prop('send', 825, 1090, .52), self.g['relocated'](context_icon(self.Icon, 12), 500, 1120, .8))
        # Anchoring line, drawn with the actor rather than a floating sticker.
        if i in [0, 2, 4]:
            a.line([(160, 1148), (440 if i != 4 else 800, 1148)], 2, '#a49b88')
        return a, b

    def ink(self, surface, icon, age, start, end, approach, active, color=False):
        paths = self.colors[id(icon)] if color else icon.paths
        traced, tip, ink = self.g['partial'](paths, (age-start)/(end-start))
        self.g['strokes'](surface, traced, color, icon.regions if color else None)
        if start <= age < end and tip is not None:
            active.append((tip, ink, approach))

    def camera(self, surface, index, age):
        # Reframe only the board artwork; headings/subtitles stay still/readable.
        u = max(0, min(1, (age-1.1)/4.6))
        ease = u*u*(3-2*u)
        if 6 <= index <= 9:
            start, end = [(1.07, 1), (1, 1.045), (1.045, 1.025), (1.025, 1)][index-6]
        else:
            start, end = (1.10, 1) if index % 2 == 0 else (1, 1.07)
        s = start + (end-start)*ease
        cx, cy = 540, 830
        if abs(s-1) < 1e-7:
            return surface
        # OpenCV's cubic transform keeps the same camera framing while avoiding
        # a full-resolution Pillow RGBA bicubic bottleneck on every frame.
        np, cv2 = self.g['np'], self.g['cv2']
        matrix = np.array([[s, 0, cx*(1-s)], [0, s, cy*(1-s)]], dtype=np.float32)
        result = cv2.warpAffine(np.asarray(surface), matrix, surface.size,
                                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
        return Image.fromarray(result)

    def build(self, t):
        g = self.g
        g['marker_count'] = 0
        index = max(0, min(len(g['frames'])-1, bisect.bisect_right(g['frame_starts'], t)-1))
        frame = g['frames'][index]
        age = t-frame['start']
        im = g['paper'].copy()
        art = Image.new('RGBA', im.size)
        active = []
        a, b = self.scenes[index]
        # The restaurant stays present across its teaching beats. Only the new
        # explanatory marks wait for each headline; inherited art is not redrawn.
        if 7 <= index <= 9:
            base = self.contexts[index]
            g['strokes'](art, self.colors[id(base)], True, base.regions)
            g['strokes'](art, base.paths)
        # Colored strokes sit beneath the existing ink, preserving contrast.
        self.ink(art, a, age, 3.65, 4.55, 'top', active, True)
        self.ink(art, b, age, 4.05, 4.92, 'bottom', active, True)
        self.ink(art, a, age, 1.18, 3.65, 'top', active)
        self.ink(art, b, age, 1.36, 4.05, 'bottom', active)
        if index == 12:
            g['write'](art, index, 'bubble-keyword', (age-5.02)/1.05, 'bottom')
        for tip, color, approach in active:
            g['pen'](art, tip, color, approach)
        art = self.camera(art, index, age)
        im.paste(art, (0, 0), art)
        # Explicit precedence: intro ends 1.05, first new ink starts 1.18;
        # picture/color ends 4.92, keyword begins 5.02. No overlap in priority.
        g['write'](im, index, 'intro', age/1.05, 'top')
        if index < 12 and t < g['meta']['cta']['start']:
            g['write'](im, index, 'title', (age-5.02)/1.05, 'bottom')
        if g['marker_count'] > 2:
            raise AssertionError(f'Three markers at {t}')
        if t >= g['meta']['cta']['start']:
            g['draw_cta'](im)
        cue = next((c for c in g['word_cues'] if c['start'] <= t-g['audio_delay'] < c['end']), None)
        if cue:
            g['caption'](im, cue['text'], g['subtitle_font'], g['meta']['caption_center_y'],
                         g['meta']['caption_font_size'], g['meta']['caption_half_height'])
        return im
