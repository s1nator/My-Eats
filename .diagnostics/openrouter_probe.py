"""Two single-input probes. Never prints credentials, headers or input texts."""
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
settings = json.loads((ROOT / '.vscode/settings.json').read_text())
KEY = settings['semanticNavigator.apiKey']
MODEL = settings['semanticNavigator.model']
URL = settings['semanticNavigator.providerUrl'].rstrip('/') + '/embeddings'

def safe(message, inputs):
    message = str(message).replace(KEY, '[REDACTED]') if KEY else str(message)
    for value in inputs:
        message = message.replace(value, '[INPUT REDACTED]')
        for line in value.splitlines():
            if len(line.strip()) >= 4:
                message = message.replace(line.strip(), '[INPUT REDACTED]')
    message = re.sub(r'(?i)(authorization|bearer|sk-or-)[^\n]*', '[REDACTED]', message)
    # Remove partial input echoes as well as complete lines.
    for value in inputs:
        for i in range(max(0, len(value) - 11)):
            fragment = value[i:i+12]
            if fragment.strip():
                message = message.replace(fragment, '[INPUT REDACTED]')
    message = re.sub(r'[\x00-\x1f\x7f]', ' ', message)
    return message[:1200]

def probe(label, text):
    body = json.dumps({'input': [text], 'model': MODEL}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY,
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            status, payload = resp.status, resp.read(2_000_000)
    except urllib.error.HTTPError as exc:
        status, payload = exc.code, exc.read(65536)
    except urllib.error.URLError:
        print(json.dumps({'probe': label, 'network_error': True})); return
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeError):
        print(json.dumps({'probe': label, 'http': status, 'non_json_response': True})); return
    out = {'probe': label, 'http': status, 'input_count': 1,
           'utf8_bytes': len(text.encode())}
    if 'error' in data:
        err = data['error']
        if isinstance(err, dict):
            out['error_message'] = safe(err.get('message', ''), [text])
            out['error_code'] = safe(err.get('code', ''), [text])
            meta = err.get('metadata', {})
            if isinstance(meta, dict):
                out['provider_name'] = safe(meta.get('provider_name', ''), [text])
                raw = meta.get('raw')
                if isinstance(raw, str):
                    try: raw = json.loads(raw)
                    except ValueError: out['provider_message'] = safe(raw, [text])
                if isinstance(raw, dict):
                    nested = raw.get('error', raw)
                    if isinstance(nested, dict):
                        out['provider_message'] = safe(nested.get('message', ''), [text])
    else:
        out['usage'] = {k: v for k, v in data.get('usage', {}).items()
                        if k in ('prompt_tokens', 'total_tokens') and isinstance(v, (int,float))}
        out['dimensions'] = len(data.get('data', [{}])[0].get('embedding', []))
    print(json.dumps(out, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    probe('short', 'hello')
    # Exact Python fallback chunk from the first HTTP 400 in this workspace.
    p = ROOT / '.venv/lib/python3.13/site-packages/_yaml/__init__.py'
    text = '// File: __init__.py\n' + p.read_text()
    probe('first_failed_chunk', text)

