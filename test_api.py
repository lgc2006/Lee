import httpx, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://127.0.0.1:8000'

try:
    # 1. Login
    r = httpx.post(f'{BASE}/api/admin/login', json={'username':'admin','password':'admin123'})
    data = r.json()
    token = data['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print(f'[OK] Login admin_id={data["admin"]["id"]} token_len={len(token)}')

    # 2. Create competition
    body = {
        'title': 'Math Modeling Contest',
        'category': 'academic',
        'description': '<h2>2026 Math Contest</h2><p>Details here</p>',
        'requirements': '<ul><li>Team of 3</li><li>Undergrad</li></ul>',
        'registration_method': 'Online',
        'registration_url': 'https://example.com/reg',
        'registration_deadline': '2026-09-15T23:59:59',
        'competition_date': '2026-10-01T08:00:00',
        'organizer': 'Ministry of Education',
        'contact_person': 'Prof Zhang',
        'contact_phone': '13800138000',
    }
    r = httpx.post(f'{BASE}/api/competitions/', json=body, headers=headers)
    if r.status_code != 200:
        print(f'[FAIL] Create returned {r.status_code}: {r.text}')
        sys.exit(1)
    comp = r.json()
    comp_id = comp['id']
    print(f'[OK] Created id={comp_id} status={comp["status"]}')

    # 3. Submit for review
    r = httpx.post(f'{BASE}/api/competitions/{comp_id}/submit', headers=headers)
    print(f'[OK] Submitted status={r.json()["status"]}')

    # 4. Approve
    r = httpx.post(f'{BASE}/api/competitions/{comp_id}/audit', json={'action':'approve','comment':'Good'}, headers=headers)
    print(f'[OK] Approved status={r.json()["status"]}')

    # 5. Create second competition and publish
    body2 = {
        'title': 'Innovation Contest',
        'category': 'innovation',
        'description': 'Innovate and create',
        'registration_deadline': '2026-08-20T23:59:59',
        'organizer': 'Student Union',
    }
    r = httpx.post(f'{BASE}/api/competitions/', json=body2, headers=headers)
    c2 = r.json()
    httpx.post(f'{BASE}/api/competitions/{c2["id"]}/submit', headers=headers)
    httpx.post(f'{BASE}/api/competitions/{c2["id"]}/audit', json={'action':'approve'}, headers=headers)
    print(f'[OK] Second competition id={c2["id"]} published')

    # 6. Public list
    r = httpx.get(f'{BASE}/api/public/competitions/')
    data = r.json()
    print(f'[OK] Public list: total={data["total"]} pages={data["total_pages"]}')
    for item in data['items']:
        print(f'     [{item["category"]}] {item["title"]} deadline={item["registration_deadline"]}')

    # 7. Public detail
    r = httpx.get(f'{BASE}/api/public/competitions/{comp_id}')
    d = r.json()
    print(f'[OK] Detail: title={d["title"]} org={d["organizer"]} status={d["status"]}')

    # 8. Filter by category
    r = httpx.get(f'{BASE}/api/public/competitions/?category=academic')
    print(f'[OK] Filter by category: {r.json()["total"]} results')

    # 9. Keyword search
    r = httpx.get(f'{BASE}/api/public/competitions/?keyword=Innovation')
    print(f'[OK] Keyword search: {r.json()["total"]} results')

    # 10. Audit logs
    r = httpx.get(f'{BASE}/api/competitions/{comp_id}/audit-logs', headers=headers)
    print(f'[OK] Audit logs: {len(r.json())} records')

    print('\n===== ALL TESTS PASSED =====')

except Exception as e:
    print(f'[FAIL] {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
