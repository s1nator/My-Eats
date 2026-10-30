from openrouter_probe import ROOT, probe
p = ROOT / '.venv/lib/python3.13/site-packages/alembic/autogenerate/api.py'
lines = p.read_text().split('\n')
text = '// File: api.py (lines 1-80)\n' + '\n'.join(lines[:80])
probe('latest_failed_file_chunk_0', text)
from tokenizers import Tokenizer
t = Tokenizer.from_file(str(ROOT / '.diagnostics/tokenizer.json'))
t.no_truncation()
shortened = text[:len(text)//2]
print('Shortened exact token count:', len(t.encode(shortened).ids), flush=True)
probe('same_chunk_shortened', shortened)
