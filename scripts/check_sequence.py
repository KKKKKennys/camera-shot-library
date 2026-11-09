"""Check a V2 cut timeline. Does not inspect images, audio or 3D geometry."""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def integer(v):
    return isinstance(v, int) and not isinstance(v, bool)

def positive_fps(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    try:
        return math.isfinite(v) and v > 0
    except OverflowError:
        # Very large JSON integers cannot be represented by the finite-float check.
        return False

def validate(plan, catalog_ids):
    if not isinstance(plan, dict):
        return ['sequence must be an object']
    errors = []
    if plan.get('schema_version') != '2.0':
        errors.append('schema_version must be 2.0')
    fps, total = plan.get('fps'), plan.get('total_frames')
    if not positive_fps(fps):
        errors.append('fps must be a finite positive number')
    if not integer(total) or total <= 0:
        return errors + ['total_frames must be a positive integer']
    segments = plan.get('segments')
    if not isinstance(segments, list) or not segments:
        return errors + ['segments must be a non-empty array']
    valid_ranges, ids = [], set()
    for i, shot in enumerate(segments):
        if not isinstance(shot, dict):
            errors.append('segment %d must be an object' % i); continue
        ident = shot.get('id')
        if not isinstance(ident, str) or not ident or ident in ids:
            errors.append('missing/duplicate segment ID at index %d' % i)
        else:
            ids.add(ident)
        cards = shot.get('cards', [])
        if not isinstance(cards, list) or not cards or any(not isinstance(c, str) or c not in catalog_ids for c in cards):
            errors.append('segment %s contains missing/unknown cards' % ident)
        start, end = shot.get('start'), shot.get('end_exclusive')
        if not integer(start) or not integer(end) or not 0 <= start < end <= total:
            errors.append('invalid frame interval for %s' % ident); continue
        valid_ranges.append((start, end, ident))
        if shot.get('fit', 'contain') not in ('contain', 'crop-approved'):
            errors.append('fit must be contain or explicitly crop-approved: %s' % ident)
        source = shot.get('source')
        if source is not None:
            if not isinstance(source, dict):
                errors.append('source must be an object: %s' % ident)
            elif not positive_fps(source.get('fps')) or source.get('fps') != fps:
                errors.append('source fps differs; resolve timing explicitly: %s' % ident)
            elif not integer(source.get('start')) or not integer(source.get('frames')) or source['start'] < 0 or source['frames'] < source['start'] + end - start:
                errors.append('source frames insufficient: %s' % ident)
        pair = shot.get('paired_layers')
        if pair is not None:
            if not isinstance(pair, list) or len(pair) < 2 or any(not isinstance(layer, dict) for layer in pair):
                errors.append('paired_layers needs at least two layer objects: %s' % ident)
            else:
                first = pair[0]
                keys = ('camera_id', 'source_start', 'fps', 'width', 'height')
                if any(k not in first for k in keys) or any(any(layer.get(k) != first.get(k) for k in keys) for layer in pair[1:]):
                    errors.append('paired layers are not aligned: %s' % ident)
                if any(
                    not isinstance(layer.get('camera_id'), str) or not layer.get('camera_id')
                    or not positive_fps(layer.get('fps')) or layer.get('fps') != fps
                    or not integer(layer.get('source_start')) or layer['source_start'] < 0
                    or any(not integer(layer.get(k)) or layer[k] <= 0 for k in ('width', 'height'))
                    for layer in pair
                ):
                    errors.append('invalid paired-layer metadata: %s' % ident)
    cursor = 0
    for start, end, ident in sorted(valid_ranges, key=lambda interval: interval[:2]):
        if start < cursor:
            errors.append('overlapping cut intervals: %s' % ident)
        elif start > cursor:
            errors.append('unassigned frames %s..%s' % (cursor, start))
        cursor = max(cursor, end)
    if cursor != total:
        errors.append('timeline does not cover total_frames')
    return errors

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('sequence', type=Path)
    args = p.parse_args()
    try:
        plan = json.loads(args.sequence.read_text(encoding='utf-8-sig'))
        ids = {c['id'] for c in json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))}
        errors = validate(plan, ids)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({'valid': not errors, 'errors': errors, 'scope': 'timeline metadata only'}, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
