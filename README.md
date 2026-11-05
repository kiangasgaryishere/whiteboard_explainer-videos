# Active Vocabulary — watercolor Reel

A Persian-language English-learning explainer using the supplied narrator recording, watercolor artwork, and progressive ink-outline reveals. Vertical 1080×1920, 25 fps. No generated voice, music, or added sound effects.

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
