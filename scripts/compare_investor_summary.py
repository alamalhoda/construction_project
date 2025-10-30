#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Dict, List

import requests


def build_session(headers: List[str]) -> requests.Session:
    s = requests.Session()
    for h in headers:
        if ':' not in h:
            print(f"Invalid header format (expected Key: Value): {h}")
            sys.exit(2)
        k, v = h.split(':', 1)
        s.headers[k.strip()] = v.strip()
    return s


def fetch_json(session: requests.Session, url: str) -> List[Dict]:
    resp = session.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json()


def normalize(data: List[Dict]) -> List[Dict]:
    keys = [
        'investor_id',
        'name',
        'participation_type',
        'total_deposits',
        'total_withdrawals',
        'net_principal',
        'total_profit',
        'grand_total',
    ]
    normalized = []
    for r in data:
        item = {k: r.get(k) for k in keys}
        normalized.append(item)
    normalized.sort(key=lambda x: x['investor_id'])
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare Investor summaries (SQL vs SSOT).')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000', help='Base URL, default: http://127.0.0.1:8000')
    parser.add_argument('--header', action='append', default=[], help='Extra HTTP header, e.g. "Authorization: Token XXX"; can be repeated')
    args = parser.parse_args()

    base = args.base_url.rstrip('/')
    url_sql = f"{base}/api/v1/Investor/summary/"
    url_ssot = f"{base}/api/v1/Investor/summary_ssot/"

    session = build_session(args.header)

    try:
        s1 = fetch_json(session, url_sql)
        s2 = fetch_json(session, url_ssot)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
        if e.response is not None:
            print(f"Response [{e.response.status_code}]: {e.response.text[:500]}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    n1 = normalize(s1)
    n2 = normalize(s2)

    equal = json.dumps(n1, ensure_ascii=False, sort_keys=True) == json.dumps(n2, ensure_ascii=False, sort_keys=True)

    print(f"Count SQL: {len(s1)} | Count SSOT: {len(s2)}")

    if equal:
        print("OK: summaries match.")
        return 0

    print("DIFF detected (showing first 20 lines)")
    a = json.dumps(n1, ensure_ascii=False, indent=2)
    b = json.dumps(n2, ensure_ascii=False, indent=2)

    # naive diff print
    for i, (la, lb) in enumerate(zip(a.splitlines(), b.splitlines())):
        if la != lb:
            print(f"- {la}")
            print(f"+ {lb}")
        if i > 20:
            break
    return 3


if __name__ == '__main__':
    sys.exit(main())


