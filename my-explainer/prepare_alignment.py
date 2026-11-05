import os, json, pathlib, sys
from faster_whisper import WhisperModel
P=pathlib.Path(__file__).parent
model=WhisperModel('small', device='cpu', compute_type='int8',cpu_threads=4,download_root=str(P/'.cache'/'speech-models'))
segments,info=model.transcribe(str(P/'source.mp3'), language='fa',word_timestamps=True,beam_size=5,initial_prompt='Passive Vocabulary. Active Vocabulary. STEP ONE CONTEXT. STEP TWO LISTEN. Can you recommend a dish? STEP THREE USE. I would recommend the pasta. رهنما. ACTIVE.')
result=[]
for s in segments:
 result.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'text':w.word} for w in s.words]})
 print(s.start,s.end,s.text,flush=True)
(P/'alignment.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
