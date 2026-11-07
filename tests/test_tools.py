import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from find_shots import search
from check_sequence import validate

CATALOG = json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
IDS = {c['id'] for c in CATALOG}

class ShotTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT/'examples/sequence.json').read_text(encoding='utf-8'))
    def test_catalog_unique_and_readable(self):
        self.assertEqual(len(CATALOG), 50); self.assertEqual(len(IDS), 50)
        for card in CATALOG:
            self.assertTrue((ROOT/card['path']).is_file())
    def test_exact_query(self):
        self.assertEqual(search(CATALOG, 'center-material-reveal')[0]['id'], 'center-material-reveal')
    def test_chinese_intent(self):
        self.assertIn('center-material-reveal', [c['id'] for c in search(CATALOG, '白模 成品')])
    def test_no_fabricated_match(self):
        self.assertEqual(search(CATALOG, 'zzzz-no-such-shot'), [])
    def test_category(self):
        rows = search(CATALOG, category='structure', limit=8)
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(c['category'] == 'structure' for c in rows))
    def test_valid_sequence(self):
        self.assertEqual(validate(self.plan, IDS), [])
    def test_gap(self):
        self.plan['segments'][1]['start'] += 1
        self.assertTrue(validate(self.plan, IDS))
    def test_overlap(self):
        self.plan['segments'][1]['start'] -= 1
        self.assertTrue(validate(self.plan, IDS))
    def test_short_source(self):
        self.plan['segments'][0]['source']['frames'] = 89
        self.assertTrue(validate(self.plan, IDS))
    def test_layer_offset(self):
        self.plan['segments'][1]['paired_layers'][1]['source_start'] = 1
        self.assertTrue(validate(self.plan, IDS))
    def test_fps_mismatch(self):
        self.plan['segments'][0]['source']['fps'] = 24
        self.assertTrue(validate(self.plan, IDS))
    def test_unknown_card(self):
        self.plan['segments'][0]['cards'] = ['not-real']
        self.assertTrue(validate(self.plan, IDS))
    def test_no_stretch(self):
        self.plan['segments'][0]['fit'] = 'stretch'
        self.assertTrue(validate(self.plan, IDS))
    def test_invalid_intervals(self):
        self.plan['segments'][0]['start'] = True
        self.assertTrue(validate(self.plan, IDS))
    def test_aligned_but_wrong_layer_fps(self):
        for layer in self.plan['segments'][1]['paired_layers']:
            layer['fps'] = 24
        self.assertTrue(validate(self.plan, IDS))
    def test_nonfinite_fps(self):
        self.plan['fps'] = float('inf')
        self.assertTrue(validate(self.plan, IDS))

if __name__ == '__main__':
    unittest.main()
