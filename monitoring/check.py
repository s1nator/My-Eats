"""Validate every graph against real VictoriaMetrics range data and generate vmui links."""
import json
import math
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

root = Path(__file__).resolve().parent
queries = json.loads((root / 'queries.json').read_text())
end = time.time()
results = {}
links = []
for title, query in queries.items():
    params = urlencode({'query': query, 'start': end - 300, 'end': end, 'step': '5s'})
    try:
        with urlopen('http://localhost:8428/api/v1/query_range?' + params, timeout=60) as response:
            data = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f'{title}: {error.read().decode()}') from error
    assert data['status'] == 'success', (title, data)
    values = [float(v) for series in data['data']['result'] for _, v in series['values']]
    finite = [v for v in values if math.isfinite(v)]
    assert finite, f'{title}: no finite samples; generate traffic first'
    results[title] = {'samples': len(finite), 'min': min(finite), 'max': max(finite), 'last': finite[-1]}
    targets = [query]
    if title == 'HTTP availability 5m (%)':
        targets.append('vector(99.5)')
    elif title == 'HTTP latency <=500ms 5m (%)':
        targets.append('vector(95)')
    elif title == 'Order success 5m (%)':
        targets.append('vector(99)')
    elif title == 'TBSLO availability 5m (%)':
        targets.append('vector(99.95)')
    elif title.startswith('SLA availability 30d'):
        targets.append('vector(99.9)')
    vm_params = {'g0.range_input': '15m', 'g0.tab': '0'}
    for i, target in enumerate(targets):
        vm_params[f'g{i}.expr'] = target
        vm_params[f'g{i}.range_input'] = '15m'
        vm_params[f'g{i}.relative_time'] = 'last_15_minutes'
        vm_params[f'g{i}.tab'] = '0'
    links.append(f'- [{title}](http://localhost:8428/vmui/#/?{urlencode(vm_params)})')
(root / 'verification.json').write_text(json.dumps({'checked_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'window_seconds': 300, 'queries': results}, ensure_ascii=False, indent=2) + '\n')
(root / 'Графики.md').write_text('# Графики VictoriaMetrics vmui\n\nСсылки открываются при работающем demo-стенде. Период — последние 15 минут.\n\n' + '\n'.join(links) + '\n')
print(json.dumps(results, ensure_ascii=False, indent=2))
