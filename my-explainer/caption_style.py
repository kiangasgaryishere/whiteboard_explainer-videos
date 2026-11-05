"""Font preflight and readable caption pills. Timing must be supplied explicitly."""
import hashlib
import json
import unicodedata
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import ImageDraw, ImageFont

ARABIC = '/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf'
LATIN = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


@lru_cache(maxsize=128)
def cached_font(path, size):
    return ImageFont.truetype(path, size)


def normalize(text):
    # Noto Sans Arabic has no U+2026: keep the punctuation using three periods.
    return unicodedata.normalize('NFC', text).replace('\u2026', '...')


@lru_cache(maxsize=None)
def coverage(path):
    with TTFont(path) as font:
        return frozenset(font.getBestCmap())


def font_path(text, preferred=None):
    rtl = any('\u0600' <= c <= '\u06ff' for c in text)
    needed = {ord(c) for c in text if not c.isspace() and unicodedata.category(c) != 'Cf'}
    candidates = ([str(preferred)] if preferred else []) + ([ARABIC, LATIN] if rtl else [LATIN, ARABIC])
    for path in candidates:
        if needed <= coverage(path):
            return path
    missing = needed - coverage(LATIN) - coverage(ARABIC)
    raise ValueError(f'Unsupported glyphs: {sorted(hex(c) for c in missing)} in {text!r}')


def load_cues(path, audio, duration, allow_estimated=False):
    data = json.loads(Path(path).read_text())
    if data.get('reviewed') is not True and not (allow_estimated and data.get('timing_status') == 'estimated-draft'):
        raise ValueError('Word timings must be reviewed before rendering.')
    digest = hashlib.sha256(Path(audio).read_bytes()).hexdigest()
    if data.get('source_sha256') != digest:
        raise ValueError('Word timings do not match the narrator recording.')
    previous = 0
    cues = data['words']
    if not cues:
        raise ValueError('The word timing file is empty.')
    for cue in cues:
        cue['text'] = normalize(cue['text'])
        if len(cue['text'].split()) != 1:
            raise ValueError(f'Expected one word: {cue}')
        if not previous <= cue['start'] < cue['end'] <= duration:
            raise ValueError(f'Invalid/overlapping word cue: {cue}')
        font_path(cue['text'])
        previous = cue['end']
    return cues


def group_cues(cues, limit=3):
    """Readable short phrases without crossing transcript lines or long pauses."""
    chunks = []
    pending = []
    def flush():
        if pending:
            chunks.append(list(pending))
            pending.clear()
    for cue in cues:
        if pending and (cue.get('line') != pending[-1].get('line') or cue['start']-pending[-1]['end'] > .5):
            flush()
        pending.append(cue)
        if len(pending) == limit or cue['text'].endswith(('.', '!', '?', '؟', '؛')):
            flush()
    flush()
    # Avoid a dangling final word: 3+1 becomes 2+2 within the same sentence.
    for previous, current in zip(chunks, chunks[1:]):
        if (len(current) == 1 and len(previous) == 3
                and current[0].get('line') == previous[-1].get('line')
                and current[0]['start']-previous[-1]['end'] <= .5
                and not previous[-1]['text'].endswith(('.', '!', '?', '؟', '؛'))):
            current.insert(0, previous.pop())
    return [{'start': c[0]['start'], 'end': c[-1]['end'],
             'text': ' '.join(w['text'] for w in c)} for c in chunks]


def caption(im, word, preferred=None, center_y=1735):
    word = normalize(word)
    size = 68
    while True:
        font = cached_font(font_path(word, preferred), size)
        if font.getlength(word) <= 740:
            break
        size -= 1
    rtl = any('\u0600' <= c <= '\u06ff' for c in word)
    d = ImageDraw.Draw(im)
    width = max(200, round(font.getlength(word)) + 100)
    cx, cy = 540, center_y
    # High contrast, compact adaptive-width background within the Reel safe area.
    d.rounded_rectangle((cx-width/2+3, cy-62+7, cx+width/2+3, cy+62+7), radius=25, fill='#cad0d3')
    d.rounded_rectangle((cx-width/2, cy-62, cx+width/2, cy+62), radius=25, fill='#20334c')
    d.text((cx, cy-3), word, font=font, fill='#ffffff', anchor='mm', direction='rtl' if rtl else 'ltr')
    d.rounded_rectangle((cx-23, cy+47, cx+23, cy+51), radius=2, fill='#e8ba53')
