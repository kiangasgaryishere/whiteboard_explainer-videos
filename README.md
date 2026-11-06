# Active Vocabulary — watercolor Reel

A Persian-language English-learning explainer using the supplied narrator recording, watercolor artwork, and progressive ink-outline reveals. Vertical 1080×1920, 25 fps. No generated voice, music, or added sound effects.

Latest captioned **draft**: [revision 13](my-explainer/out/diagram-v13.mp4) / [ZIP](my-explainer/out/diagram-v13.zip). Camera movement reduced another 40% from V12 (58% below V11 overall). Static headings, pen speed, scene timing, narration and captions are retained. Base speech/caption timing remains **estimated and unverified**.

## Watch or download

- [Full-length narrated draft](my-explainer/out/narrated-visual-draft.mp4)
- [Downloadable video ZIP](my-explainer/out/my-explainer-video.zip)
- [20-second silent motion preview](my-explainer/out/watercolor-motion-preview.mp4)
- [Approved minimal watercolor style](my-explainer/previews/style-experiments/watercolor-minimal-approved.png)
- [Original storyboard](my-explainer/previews/storyboard.png)

**Status:** the narrated video is a draft. It does **not** contain synchronized Persian captions. Exact scene/voice synchronization, timed English examples, and the final J/L-cut edit remain unfinished. The original audio's playable duration is 93.393696 seconds; the narrated draft's container duration matches it. Speech alignment is blocked in the original cloud environment by network access to the speech-model download host. Do not describe this as the finished captioned Reel.

## Project files

`my-explainer/` contains the original `source.mp3`, supplied `transcript.md`, approved `brief.md`, scene-grouped `script.json`, generated watercolor assets, previews, and all rendered outputs. Original study-board drawings and legacy renderer files are retained for project history; `watercolor_motion.py` is the current renderer. `voice.json` documents the original recording; it is not a synthesis configuration for the upstream audio generator.

## Visual revision 2

`kinetic_render.py` implements the requested faster visual treatment: 26 beats, a new text/focus event every 3.6 seconds, visible black/blue/green markers, progressive Persian/English text reveal, traced illustration outlines, watercolor fill, and the original narration. The visual edit is controlled by `kinetic_edit.json`. These timings are provisional editorial cues, **not verified subtitle timing**.

```bash
python3 my-explainer/kinetic_render.py --preview 10.8
python3 my-explainer/kinetic_render.py
```

The new output is `my-explainer/out/kinetic-marker-v2.mp4`; the earlier drafts are retained. This revision increases teaching text as requested and supersedes the earlier sparse-text treatment. It does not resolve the outstanding speech-alignment dependency.

## Visual revision 3 — complete drawn diagrams

`diagram_render.py` replaces the raster illustration approach with 26 simple, entirely authored vector drawings arranged into 13 vertical two-node charts. A marker draws every intended outline, then a colored marker fills regions with clipped strokes, then the labels are written. Illustrations and text have separate fixed vertical bands. The original audio remains the only sound.

```bash
python3 my-explainer/diagram_render.py --preview 14.4
python3 my-explainer/diagram_render.py
```

Outputs: `my-explainer/out/diagram-v3.mp4` and a separately packaged `diagram-v3.zip`. `diagram_v3.json` records the layout, drawing phases and short labels; `kinetic_edit.json` supplies the inherited provisional editorial beats. These are on-board teaching labels, not verified speech-aligned subtitles. The full export adjusts the last video packet to match the original recording's playable length.

## Visual revision 4 — notebook paper, bold type, one marker

```bash
python3 my-explainer/diagram_render.py --revision 4
python3 my-explainer/diagram_render.py --revision 4 --style-still 21.35 --sample-word معنی
```

Revision 4 uses a generated notebook-paper texture based on the supplied reference, larger bold headlines, glyph-coverage preflight and punctuation normalization, and sequential marker actions. Every rendered frame checks that at most one marker is drawn. The missing square in `می‌دونی…` came from U+2026 (ellipsis), which the Arabic font does not cover; it was not an emoji. The new font handling prevents silently rendering unsupported characters.

**Caption status:** the one-word caption layout is implemented, but verified word timestamps are still unavailable. The standard `diagram-v4.mp4` is a visual revision without spoken captions. `previews/caption-style-sample.png` demonstrates the proposed caption background with a sample word; it is a still typography sample, not an aligned subtitle export.

To render actual word captions once timings have been verified:

```bash
python3 my-explainer/diagram_render.py --revision 4 --word-captions my-explainer/word-captions.json
```

The timing file must contain `reviewed: true`, `source_sha256` matching `source.mp3`, and a nonempty `words` array of `{start, end, text}` entries. Each entry must be one word, inside the recording's playable duration, chronologically ordered and nonoverlapping. Unreviewed, stale or invalid timing files are rejected. No estimated timing file is supplied as if verified. Speech-model downloads remain blocked by the cloud network policy; the recording itself needs no additional voice generation.

## Visual revision 5 — pictures first, fewer words, longer holds

```bash
python3 my-explainer/diagram_render.py --revision 5 --preview 14
python3 my-explainer/diagram_render.py --revision 5
```

The 13 variable-length frames each remain for 6.4–7.8 seconds. A large primary drawing, a connector and a smaller supporting drawing form one continuous composition. All image construction/coloring finishes before the only on-board keyword band starts writing. Repeated explanations and the old 3.6-second text swaps are removed. The two English restaurant sentences remain as essential teaching examples. The notebook-paper texture, bold glyph-safe text, original recording and one active marker are preserved.

`diagram_v5.json` defines the actual picture cuts, frame durations, keywords, illustration pairs and provisional audio references. Some picture cuts lead those references (planned L-cuts); others follow them (planned J-cuts). **These are editorial offsets against estimated reference points, not verified semantic speech alignment.** Narration remains continuous and unmodified; no artificial pauses or time stretching were introduced.

Outputs: `my-explainer/out/diagram-v5.mp4`, `diagram-v5-preview.mp4` and `diagram-v5.zip`. Earlier versions remain available. This is the latest visual edit, not a claim that the outstanding word-caption alignment has been completed.

## Revision 6 — explicit comment CTA, Shabnam, draft subtitles

The closing card now reads **کلمهٔ ACTIVE را کامنت کن** rather than showing ACTIVE alone. The final picture contains an ACTIVE comment bubble and a send icon. The CTA appears from the provisional closing-offer anchor at 83.73 seconds and remains through the end.

Official unmodified Shabnam Bold and Medium font files are bundled in `my-explainer/assets/fonts/` with the original license and upstream commit provenance. Bold is used for Persian headlines/CTA; Medium for Persian subtitles. Glyph coverage is checked and fallback fonts remain available.

```bash
python3 my-explainer/estimate_caption_draft.py
python3 my-explainer/diagram_render.py --revision 6 \
  --word-captions my-explainer/word-captions.estimated.json \
  --allow-estimated-captions
```

**Timing limitation:** speech-model access still returned HTTP 403. Instead of withholding all subtitles, this draft displays all 238 words of the supplied transcript. Line anchors were inferred from script order and detected pauses; word durations were weighted over voiced regions. This is not ASR or forced alignment and has not been verified by listening against every word. Errors and drift remain possible. It must not be described as a final synchronized subtitle track.

`word-captions.estimated.json` retains `reviewed: false` and `timing_status: estimated-draft`; normal rendering rejects it without the explicit draft flag. The `.srt` sidecar is provided for review/editing. Never mark timings reviewed merely to bypass validation. The ZIP includes the MP4, estimated timing sidecars and a status note. Original audio content, speed and duration are preserved.

## Revision 7 — opposing marker angles, short phrases, picture lead

```bash
python3 my-explainer/diagram_render.py --revision 7 \
  --word-captions my-explainer/word-captions.estimated.json \
  --allow-estimated-captions
```

Two distinct marker bodies alternate: the pale marker approaches from the upper left, and the shorter cream marker from the lower right. Only one is active at a time. Drawing/coloring tasks and alternate keyword frames use the opposing approaches.

Subtitles now show up to three words per box (89 groups), respecting transcript lines, punctuation and long pauses. Dangling final words are balanced into 2+2 groups rather than 3+1; the only single-word exception is the standalone utterance «دیدی؟». The caption center moves from y=1735 to y=1543, exactly 192px or 10% of the canvas height. Keywords and the compact CTA card move upward as well so they do not overlap subtitles. Shabnam and the paper texture are retained.

The original narrator recording is delayed by exactly one second; picture starts remain unchanged. Captions receive the same delay. No source audio is trimmed or stretched: the output is therefore **94.393696 seconds**, one second longer than V6. The last picture holds for the extra second and every frame still lasts 6–8 seconds. This global picture lead supersedes the earlier mixed lead/lag offsets; source semantic boundaries are still provisional.

`captions-v7.estimated.srt` and `.json` contain grouped captions in output-video time, including the +1s delay. The renderer still takes the original word-level timing file as input and performs grouping/offset itself. Do not feed the already-shifted sidecar back in as source timings. Base timing remains an estimated draft requiring review.

## Revision 8 — truly simultaneous drawing and a quicker hook

```bash
python3 my-explainer/diagram_render.py --revision 8 \
  --word-captions my-explainer/word-captions.estimated.json \
  --allow-estimated-captions
```

Both markers now work at the same time. Nine scenes pair the upper marker's main drawing/text with the lower marker's supporting drawing/color. Four scenes divide the primary figure into upper/lower paths so both markers draw different sections of the same figure. Split-path length is checked to ensure no authored lines disappear. Keyword writing overlaps the other marker's illustration work. Small, occasional emphasis strokes vary the ending of a scene rather than repeating a full-frame reset.

The renderer enforces a maximum of two markers and records actual 0/1/2-marker frame counts in `previews/diagram-v8-marker-activity.json`, so concurrency is measured, not merely permitted. Subtitle type shrinks from 68px to 58px and the background from 124px to 108px high; the raised caption position and short phrase grouping remain.

The global narration delay is reduced from 1s to **0.5s**. The full original recording is preserved, giving **93.893696s** total duration. The initial silent lead is only half a second. Some picture cuts were moved toward inferred clause/pause boundaries; CONTEXT and RECOMMEND labels were reassigned to better match lesson order. These are editorial refinements against unverified anchors, not a claim of precise semantic J/L alignment. Subtitle sidecars include the same +0.5s playback offset. All 13 picture frames remain within 6–8 seconds.

## Setup

Use Python 3.12 and FFmpeg/ffprobe. The renderer uses Debian/Ubuntu fonts from `fonts-noto-core` and `fonts-dejavu-core` (Noto Sans Arabic Bold and DejaVu Sans Bold); install those fonts or update the font paths when using another operating system.

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 my-explainer/watercolor_motion.py
python3 my-explainer/watercolor_motion.py --narrated-draft
```

The default command regenerates the silent motion preview. `--narrated-draft` uses provisional scene boundaries and no captions. These commands overwrite their named generated videos. The renderer's fixed-frame-rate export may round the last frame; the checked-in narrated draft was remuxed to shorten its final video packet to the exact playable source duration.

## Finish synchronized captions

```bash
. .venv/bin/activate
python3 -m pip install -r requirements-alignment.txt
python3 my-explainer/prepare_alignment.py
```

This downloads the multilingual Faster Whisper small model and transcribes locally with word timestamps. Model access requires `huggingface.co`, `*.huggingface.co`, and `*.hf.co` in restricted cloud environments. These domains were saved in the onboarding draft, but were not active during production.

Compare the resulting `alignment.json` against the supplied transcript, especially mixed Persian/English phrases. Preserve the supplied text rather than accepting recognition substitutions. Build and review `my-explainer/watercolor-edit.json` with this structure:

```json
{
  "scenes": [
    {"asset": "study", "start": 0, "end": 16.3, "title": ""}
  ],
  "captions": [
    {"start": 0.3, "end": 2.4, "text": "متن زیرنویس"}
  ]
}
```

The numbers above illustrate the schema, not verified timing. Valid assets: `study`, `passive`, `active`, `restaurant`, `package`. Caption cues should be short enough for two lines. After timings are reviewed, run `python3 my-explainer/watercolor_motion.py --final`, inspect the video and audio endpoints with ffprobe, and verify Persian shaping, English highlights, readable safe areas, and timing across transitions.

## Upstream tools and attribution

`tools/whiteboard-video/` preserves the original [whiteboard-video-skill](https://github.com/Matteoikarieth96/whiteboard-video-skill) at commit `75c7825e3ccaf33be933a143c561acab1deb74a6`, with its MIT license and bundled font license. Its Node dependencies can be installed with `npm ci --prefix tools/whiteboard-video/scripts`. The current watercolor renderer does not require Chromium or these Node dependencies. The upstream Chromium renderer was blocked by the managed browser's local-file policy during onboarding.

Watercolor scene artwork was generated with OpenAI image generation using the approved style references. Original filenames are recorded in `my-explainer/assets/manifest.json`. Machine-specific paths in the production brief are historical provenance; use the relative repository paths above for current work.

## Visual revision 9 — richer authored illustrations and a visual hook

`art_direction.py` supplies curved, expressive clothed characters, perspective page edges, material hatching, restaurant tableware, headphones and pasta details. Each scene gains a relevant contextual inset: recognition/magnifier, hesitation clock, restaurant awning, menu, spoken example, practice microphone or weekly gift. The inset target is 30% of the existing illustration bounding-box footprint (measured 27.2–30%, mean about 29.8%); this measures layout footprint, not painted pixels. Keywords and subtitle safe areas remain separate.

The first four seconds show a worried learner and word cards, a blocked speech path with a red lock/cross, and “بلدی، ولی نمی‌گی؟”. This visual question builds on the existing narration; no new voice, music or SFX are added. Two opposing markers draw in parallel, then color clipped regions and write the keyword. The 13 scene windows and original voice remain; the export includes a 0.5s picture lead and lasts 93.893696s.

```sh
PYTHONPATH=/workspace/whiteboard-tools python3 my-explainer/diagram_render.py --revision 9 \
  --word-captions my-explainer/word-captions.estimated.json --allow-estimated-captions
# Add --preview 6.9 for the opening, or --art-sheet for the 13-scene review sheet.
```

Outputs: `out/diagram-v9.mp4`, `out/diagram-v9.zip`, `previews/diagram-v9-art-sheet.png`, art footprint metrics and per-frame marker counts. Caption text is preserved, but inherited speech timings and semantic cut anchors remain estimated/unreviewed.

## Visual revision 10 — headline, picture, keyword

The newer request supersedes picture-first sequencing. Each new scene writes a short curiosity headline (0–1.05s), draws its new illustrations with two opposing markers (outlines 1.18–4.05s, coloring through 4.92s), then writes the keyword (5.02–6.07s). The final ACTIVE keyword is written inside its speech bubble. Previously drawn restaurant context persists across four teaching scenes; new explanatory marks wait for the opening headline. The existing comment CTA remains above the subtitle band.

`direction_v10.py` directs a recurring learner with the same hair, face and clothing, more adult proportions, and changing thoughtful/confident poses. The waiter is distinguished by glasses, moustache and vest. Restaurant composition remains in place while context, listening, question and answer develop. Camera reframing affects only artwork; headings, CTA and captions stay still. Marker bodies have highlights and soft shadows. Curved line art and transparent color strokes remain authored vectors.

**Background provenance:** the original inline paper image was visible in chat but not exposed as a downloadable file in this workspace. `assets/cream-paper-reference-reconstruction.png` is an AI reconstruction based on that image, not the exact supplied pixels. It replaces the lined notebook background. No new voice, music or sound effects are added.

```sh
PYTHONPATH=/workspace/whiteboard-tools python3 my-explainer/diagram_render.py --revision 10 \
  --word-captions my-explainer/word-captions.estimated.json --allow-estimated-captions
# Add --art-sheet for the scene review sheet, or --preview 14 for the opening.
```

Review images: `previews/diagram-v10-opening-sequence.jpg` and `diagram-v10-art-sheet.png`. Pixel checks of actual rendered frames confirm that new artwork does not appear before the headline and keywords do not appear before picture completion. The prior restaurant context is intentionally retained. Original narration remains complete with the previously requested 0.5s delay: output duration 93.893696s. Subtitle cues, teaching scene boundaries and semantic J/L anchors are inherited estimates, not newly verified speech alignment.

V10 English examples are written first as the opening headline and remain for their full 6.6s/7s scene windows; the shorter RECOMMEND / USE keyword follows the drawing. This avoids introducing a full teaching sentence only at the end of the scene.

## Visual revision 11 — instant headings and directed camera beats

Black headings now appear complete on scene entry; no heading is written by a marker. Illustration starts at 0.18s. Actual pen traversal durations are multiplied by 1.08 (about 7.4% lower path speed), and keywords also write 8% more slowly after the picture. Standard drawing ends at 4.2192s, followed by keyword lettering from 4.3272–5.4612s. This supersedes V10's animated opening headlines.

`direction_v11.py` extends the V10 art/character system. The first four seconds establish the question immediately, draw the learner's worried expression and speech bubble early, and send word cards toward a red speech barrier before they recoil. Camera keyframes move from notebook focus toward the learner and pull out to reveal the contrast. Other shots use a worried-learner push-in, passive/active reframing, restaurant establishing view, listening detail, stable English-example frames and a confident-learner callback at the CTA. Text and subtitle positions remain fixed. Semantic camera movement is driven by the existing scene plan; it does not establish verified speech synchronization.

```sh
PYTHONPATH=/workspace/whiteboard-tools python3 my-explainer/diagram_render.py --revision 11 \
  --word-captions my-explainer/word-captions.estimated.json --allow-estimated-captions
# --art-sheet reviews all scenes; --preview 6.9 reviews the opening.
```

Review: `previews/diagram-v11-hook-sequence.jpg`, `diagram-v11-art-sheet.png`, direction validation and per-frame marker counts. The cream background remains an AI reconstruction of the inline user reference; exact original background pixels were unavailable. Original audio is complete with the previously requested 0.5s delay; no added music/SFX. Caption and semantic J/L timing remain inherited, unreviewed estimates.

## Visual revision 12 — 30% gentler camera movement

V12 sets `camera_motion_strength: 0.7`. The camera blends its affine transform 70% toward the V11 transform from the identity: both zoom deviation from 1× and horizontal/vertical translation are reduced by exactly 30%. For example, the opening zoom changes from 1.32× to 1.224×. Shot timing, easing, pen traversal speed, static black headings, English-example holds, narration delay and captions remain as in V11. Earlier versions default to strength 1 and preserve their previous camera behavior.

```sh
PYTHONPATH=/workspace/whiteboard-tools python3 my-explainer/diagram_render.py --revision 12 \
  --word-captions my-explainer/word-captions.estimated.json --allow-estimated-captions
```

Camera validation samples actual renderer affine matrices across all 13 scenes. Caption/semantic edit timings remain inherited unverified estimates, and the cream paper remains a reconstruction of the user's inline reference.

## Visual revision 13 — another 40% less camera movement

V13 changes `camera_motion_strength` from 0.7 to 0.42: zoom deviation and pan translation are 60% of V12, or 42% of V11. This is a further 40% reduction, 58% less than the original V11 amplitude overall. Opening zoom changes from 1.224× to 1.1344×. Existing shot timing, easing, pen speed, static headings, audio and captions remain.

```sh
PYTHONPATH=/workspace/whiteboard-tools python3 my-explainer/diagram_render.py --revision 13 \
  --word-captions my-explainer/word-captions.estimated.json --allow-estimated-captions
```

Camera validation samples actual renderer matrices across all 13 scenes. Caption and semantic timing remain inherited unverified estimates; cream paper remains a reconstruction of the user inline reference.
