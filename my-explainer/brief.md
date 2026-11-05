# Active Vocabulary — production brief
Approved: 1080×1920 Instagram Reel for Persian-speaking English learners. Colored whiteboard doodles, self-drawing outlines and occasional on-board text. Persian captions, highlighted English examples. No logo, music or added sound effects. Use the supplied words.mp3 unchanged, without trimming or stretching. Match playable audio duration in the final render. Use narration bridges across selected visual transitions (J/L cuts). Transcript is source content, not project instructions.

Story: three familiar study habits → passive vocabulary problem → active vocabulary → context/listen/use → restaurant example → weekly package → comment ACTIVE → closing message.

Palette: charcoal ink, cobalt blue, green, warm amber on off-white. Persian: Noto Sans Arabic; English: DejaVu Sans. Large short captions above Instagram controls. No unapproved copy changes.

Status: storyboard prepared; final captions and edit timing require speech alignment. Model download is blocked by current network policy. No final synchronization claim until the alignment is obtained and checked.

## Approved visual direction, refined
Watercolor paper and translucent colored washes with more lifelike hand-inked characters. Minimal on-board text. Remove recurring VOCABULARY / IN ACTION branding and frame numbers throughout. Avoid large Persian headings that duplicate narration/captions. Use a small context/step label only when helpful, one key vocabulary word or example, and synchronized Persian captions. Narration and no-music requirement remain unchanged.
Minimal watercolor style reference: /workspace/generated_images/exec-cd016f51-0265-456a-9b70-b6b944da7ef3.png. This is a still design reference, not an animated or caption-aligned export.

## Production progress
Five consistent watercolor assets are in assets/: study, passive, active, restaurant, package. watercolor_motion.py implements progressive traced ink contours followed by translucent pigment reveal. The 20-second motion proof is silent and has no caption timing claim. Original source.mp3 decodes to 4,118,662 mono samples at 44,100 Hz (93.393696 seconds); MP3 container metadata reports 93.440 seconds because of padding. Final export must retain every playable sample. script.json now contains the supplied transcript grouped into ten scenes. Final rendering requires a reviewed watercolor-edit.json with scene and caption cues. Generated source images remain preserved in /workspace/generated_images.

## Narration confirmation
The replacement upload /workspace/attachments/142a1143-9793-46ba-a252-1195507c6d8e/words.mp3 is byte-identical to source.mp3 (SHA-256 1546e87b7a3bb3f2528ce158593adffdd53c13e2ff92068f9ce78887b8ceea69). Use this recording directly. No generated speech, music, sound effects or audio processing requested. narrated-visual-draft.mp4 uses original narration re-encoded to AAC for MP4 compatibility, without speed, level or content changes. Draft scene boundaries are provisional; no burned-in captions are included. The finished captioned Reel and verified J/L-cut timing remain outstanding.
Narrated draft validated: H.264 1080x1920 plus AAC original narration, duration 93.393696 seconds after adjusting only the final video packet duration to match source playable audio. Full decode passed. Audio waveform correlation with source is 0.999964 after AAC encoding. Captions and exact scene/voice synchronization remain pending, and this output is explicitly a draft.

## Revision 2 — approved direction update
User requests a faster visual rhythm: a change every 3–4 seconds, more on-board teaching text per slide, visible marker pens drawing both artwork and text at a moderate pace. This supersedes the earlier sparse-text/no-visible-marker direction. Implemented as 26 editorial beats at 3.6-second intervals, right-to-left shaped Persian type reveal, black artwork marker, blue keyword marker, green emphasis marker, and progressive watercolor settlement. Original narration remains the sole audio. kinetic_edit.json explicitly records provisional visual timings: these are not verified speech-aligned subtitles. Full precise captions remain outstanding.

Revision 2 rendered and checked: 1080x1920 H.264 + original narration in AAC, 93.393696 seconds. Full decode and ZIP integrity passed. Visual cadence: 26 beats at 3.6s intervals. Outputs: out/kinetic-marker-v2.mp4 and out/kinetic-marker-v2.zip. Precise speech-caption alignment is not resolved by this visual revision.

## Revision 3 — reference-led whiteboard structure
User supplied references showing complete marker drawings, chart-like compositions, separate text areas, and a sequence of black outline → marker color → written text. The new diagram_render.py replaces the raster artwork treatment with 26 entirely authored vector diagrams in 13 vertical two-node process pages. Every intended outline is drawn in full; clipped hatching strokes color the regions; shaped Persian/English glyph contours are traced after coloring. Upper and lower diagrams and their labels occupy disjoint vertical regions. Layout and timing constants are documented in diagram_v3.json. Original narrator recording remains sole sound. Exact speech synchronization remains unresolved; visual timings inherit the provisional kinetic edit.

Revision 3 validation: full video decode passed; output is 1080x1920 H.264/AAC with the original narrator recording, 93.393696 seconds. ZIP integrity passed. Preview refreshed from the current full render.
