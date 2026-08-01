def test_list_keys_limit_returns_subset(cli, kms, tmp_path):
    # Seed prerequisite state: create a few keys so listing is non-empty.
    created_ids = []
    for _ in range(3):
        resp = kms.rpc("CreateKey", {"Description": "list-keys-test"})
        created_ids.append(resp["KeyMetadata"]["KeyId"])

    # Run the command under test with --limit 1.
    result = cli("kms", "list-keys", "--limit", "1")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    keys = payload.get("Keys", [])
    # --limit 1 must return no more than 1 key.
    assert len(keys) <= 1
    for k in keys:
        assert "KeyId" in k

    # Independent read: the full ListKeys via raw RPC must include the seeded keys.
    all_ids = set()
    marker = None
    while True:
        req = {}
        if marker:
            req["Marker"] = marker
        r = kms.rpc("ListKeys", req)
        for k in r.get("Keys", []):
            all_ids.add(k["KeyId"])
        if r.get("Truncated") and r.get("NextMarker"):
            marker = r["NextMarker"]
        else:
            break

    for kid in created_ids:
        assert kid in all_ids