"""Find shot cards by intent, ID or category. Reads the bundled catalog only."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def search(catalog, query='', category=None, limit=3):
    terms = re.findall(r'[^\s,，]+', query.casefold())
    rows = []
    for card in catalog:
        if category and category not in (card['category'], card['category_name']):
            continue
        haystack = ' '.join(str(card.get(k, '')) for k in ('id', 'title', 'goal', 'category_name')).casefold()
        score = sum(2 if term in card['title'].casefold() or term == card['id'] else 1 for term in terms if term in haystack)
        if terms and not score:
            continue
        rows.append((score, card))
    rows.sort(key=lambda row: (-row[0], row[1]['id']))
    return [row[1] for row in rows[:limit]]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('query', nargs='?', default='')
    p.add_argument('--category')
    p.add_argument('--limit', type=int, default=3)
    p.add_argument('--json', action='store_true')
    args = p.parse_args()
    if not 1 <= args.limit <= 50:
        p.error('--limit must be between 1 and 50')
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8-sig'))
    rows = search(catalog, args.query, args.category, args.limit)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            print('%s | %s | %s\n  %s\n  %s' % (row['id'], row['title'], row['category_name'], row['goal'], row['path']))
        if not rows:
            print('No matching cards. Try a shorter keyword or a category.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
