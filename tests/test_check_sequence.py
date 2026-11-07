import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_sequence import validate

CARD = 'silhouette-establish'
IDS = {CARD}


def sequence():
    return {
        'schema_version': '2.0',
        'fps': 1,
        'total_frames': 1,
        'segments': [{
            'id': 'shot',
            'cards': [CARD],
            'start': 0,
            'end_exclusive': 1,
            'source': {'start': 0, 'frames': 1, 'fps': 1},
            'paired_layers': [{
                'camera_id': 'Camera_A',
                'source_start': 0,
                'fps': 1,
                'width': 1,
                'height': 1,
            } for _ in range(3)],
        }],
    }


class SequenceValidationTests(unittest.TestCase):
    def test_tied_intervals_do_not_compare_segment_ids(self):
        for ident in (None, False, 1, [], {}, ''):
            with self.subTest(ident=ident):
                plan = sequence()
                other = copy.deepcopy(plan['segments'][0])
                other['id'] = ident
                plan['segments'].append(other)
                errors = validate(plan, IDS)
                self.assertTrue(any('segment ID' in error for error in errors))
                self.assertTrue(any('overlapping cut intervals' in error for error in errors))

    def test_fps_rejects_invalid_types_and_values_everywhere(self):
        invalid = (None, True, False, 0, -1, '', '1', [], {},
                   float('nan'), float('inf'), float('-inf'), 10 ** 1000)
        for field in ('plan', 'source', 'paired_layers'):
            for value in invalid:
                with self.subTest(field=field, value=value):
                    plan = sequence()
                    shot = plan['segments'][0]
                    target = {'plan': plan, 'source': shot['source'],
                              'paired_layers': shot['paired_layers'][-1]}[field]
                    target['fps'] = value
                    self.assertTrue(validate(plan, IDS))

    def test_all_layer_metadata_is_validated(self):
        invalid = {
            'camera_id': (None, False, 1, '', [], {}),
            'source_start': (None, False, 0.0, -1, '0', [], {}),
            'width': (None, True, 1.0, 0, -1, '1', [], {}),
            'height': (None, True, 1.0, 0, -1, '1', [], {}),
        }
        for index in range(3):
            for field, values in invalid.items():
                for value in values:
                    with self.subTest(index=index, field=field, value=value):
                        plan = sequence()
                        plan['segments'][0]['paired_layers'][index][field] = value
                        errors = validate(plan, IDS)
                        self.assertIn('invalid paired-layer metadata: shot', errors)

    def test_missing_layer_fields_are_invalid(self):
        for index in range(3):
            for field in ('camera_id', 'source_start', 'fps', 'width', 'height'):
                with self.subTest(index=index, field=field):
                    plan = sequence()
                    del plan['segments'][0]['paired_layers'][index][field]
                    errors = validate(plan, IDS)
                    self.assertIn('invalid paired-layer metadata: shot', errors)
                    self.assertIn('paired layers are not aligned: shot', errors)

    def test_valid_numeric_fps_and_optional_metadata_remain_supported(self):
        for fps in (1, 1.0, 23.976, 30, 30.0, 1e308):
            with self.subTest(fps=fps):
                plan = sequence()
                plan['fps'] = fps
                plan['segments'][0]['source']['fps'] = fps
                for layer in plan['segments'][0]['paired_layers']:
                    layer['fps'] = fps
                self.assertEqual(validate(plan, IDS), [])
        plan = sequence()
        plan['segments'][0]['source']['fps'] = 1.0
        plan['segments'][0]['paired_layers'][-1]['fps'] = 1.0
        self.assertEqual(validate(plan, IDS), [])
        for optional in ('source', 'paired_layers'):
            plan['segments'][0][optional] = None
        self.assertEqual(validate(plan, IDS), [])
        for optional in ('source', 'paired_layers'):
            del plan['segments'][0][optional]
        self.assertEqual(validate(plan, IDS), [])

    def test_malformed_json_field_types_return_errors(self):
        invalid_shapes = (None, False, 1, 'bad', [])
        for value in invalid_shapes:
            with self.subTest(plan=value):
                self.assertTrue(validate(value, IDS))
        fields = {
            'schema_version': (None, False, 2.0, [], {}),
            'total_frames': (None, True, 1.0, '1', [], {}),
            'segments': (None, False, 1, 'bad', {}, [], [None], [[]]),
        }
        for field, values in fields.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    plan = sequence()
                    plan[field] = value
                    self.assertTrue(validate(plan, IDS))
        fields = {
            'id': (None, False, 1, [], {}),
            'cards': (None, False, 1, CARD, {}, [], [None], [[]], [{}]),
            'start': (None, False, 0.0, '0', [], {}),
            'end_exclusive': (None, True, 1.0, '1', [], {}),
            'fit': (None, False, 1, [], {}),
            'source': (False, 1, 'bad', []),
            'paired_layers': (False, 1, 'bad', {}, [], [{}], [{}, None]),
        }
        for field, values in fields.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    plan = sequence()
                    plan['segments'][0][field] = value
                    self.assertTrue(validate(plan, IDS))

    def test_source_frame_fields_require_integers(self):
        for field in ('start', 'frames'):
            for value in (None, True, False, 1.0, -1, '1', [], {}):
                with self.subTest(field=field, value=value):
                    plan = sequence()
                    plan['segments'][0]['source'][field] = value
                    self.assertIn('source frames insufficient: shot', validate(plan, IDS))

    def test_unordered_valid_segments_still_cover_timeline(self):
        plan = sequence()
        plan['total_frames'] = 3
        plan['segments'] = [
            {'id': str(start), 'cards': [CARD], 'start': start,
             'end_exclusive': start + 1} for start in (2, 0, 1)
        ]
        self.assertEqual(validate(plan, IDS), [])


class SequenceCliTests(unittest.TestCase):
    def run_cli(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sequence.json'
            path.write_text(content, encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/check_sequence.py'), str(path)],
                text=True, capture_output=True, check=False,
            )
        self.assertEqual(result.stderr, '')
        payload = json.loads(result.stdout)
        self.assertEqual(payload['scope'], 'timeline metadata only')
        return result.returncode, payload

    def test_valid_sequence_with_bom(self):
        code, payload = self.run_cli('\ufeff' + json.dumps(sequence()))
        self.assertEqual(code, 0)
        self.assertEqual(payload['errors'], [])
        self.assertTrue(payload['valid'])

    def test_invalid_sequences_return_json_without_tracebacks(self):
        tied = sequence()
        other = copy.deepcopy(tied['segments'][0])
        other['id'] = {}
        tied['segments'].append(other)
        invalid_layer = sequence()
        invalid_layer['segments'][0]['paired_layers'][-1]['width'] = True
        samples = [json.dumps(tied), json.dumps(invalid_layer), '{', '[]']
        for value in (float('nan'), float('inf'), 10 ** 1000):
            plan = sequence()
            plan['fps'] = value
            samples.append(json.dumps(plan))
        for content in samples:
            with self.subTest(content=content[:80]):
                code, payload = self.run_cli(content)
                self.assertEqual(code, 1)
                self.assertTrue(payload['errors'])
                self.assertFalse(payload['valid'])


if __name__ == '__main__':
    unittest.main()
