"""Check the committed aggregate example and its reported findings."""
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
real=json.loads((ROOT/'results/anthropic_aggregate.json').read_text())
fake=json.loads((ROOT/'results/synthetic_checks.json').read_text())
assert real['conversations']==1250 and real['user_turns']==14495
for result in [real,fake]:
    for scenarios in result['cohorts'].values():
        for value in scenarios.values():
            assert all(r['n']>=100 and math.isfinite(r['mean_words']) for r in value['rows'])
            assert all(set(r)=={'turn','n','mean_words','median_words'} for r in value['rows'])
            assert all(v is None or v['turn'] in value['detection']['eligible_turns']
                       for v in value['detection']['methods'].values())
expected={
    'all_turns':[10,14,4,4],
    'exclude_first':[10,14,4,4],
    'exclude_final':[4,14,4,4],
    'fixed_cohort_10':[10,10,4,4],
}
labels={'all_turns':'All turns','exclude_first':'Exclude first response',
        'exclude_final':'Exclude each final response','fixed_cohort_10':'Same conversations through turn 10'}
findings=(ROOT/'docs/FINDINGS.md').read_text(encoding='utf-8')
for key,values in expected.items():
    actual=[v['turn'] for v in real['cohorts']['all'][key]['detection']['methods'].values()]
    assert actual==values
    assert '| '+labels[key]+' | '+' | '.join(map(str,values))+' |' in findings
assert all(v['turn']==7 for v in fake['cohorts']['injected_decline']['all_turns']['detection']['methods'].values())
assert all(v is None for v in fake['cohorts']['flat']['all_turns']['detection']['methods'].values())
quality=json.loads((ROOT/'results/data_quality.json').read_text())
assert quality['sql_python_aggregation_match'] is True
assert (ROOT/'demo/data.js').read_text(encoding='utf-8')=='window.EXAMPLE_DATA = '+json.dumps({'public':real,'synthetic':fake})+';\n'
print('Aggregate cell suppression, reported findings, synthetic controls, and demo data agree.')
