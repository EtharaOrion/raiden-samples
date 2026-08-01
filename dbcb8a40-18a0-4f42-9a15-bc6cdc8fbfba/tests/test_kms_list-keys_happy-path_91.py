def test_list_keys_limit_happy_path(cli, kms):
    # Seed prerequisite state: create a couple of keys
    key1 = kms.rpc("CreateKey", {"Description": "list-keys-test-1"})
    id1 = key1["KeyMetadata"]["KeyId"]
    key2 = kms.rpc("CreateKey", {"Description": "list-keys-test-2"})
    id2 = key2["KeyMetadata"]["KeyId"]

    # Run the command under test
    result = cli("kms", "list-keys", "--limit", "1")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    assert "Keys" in payload
    assert isinstance(payload["Keys"], list)
    # limit of 1 must return no more than 1 item
    assert len(payload["Keys"]) <= 1
    for entry in payload["Keys"]:
        assert "KeyId" in entry

    # Independent read: seeded keys must exist in the full listing.
    # ListKeys paginates (default page size), and the backend accumulates keys
    # across the session, so walk every page before asserting membership.
    all_ids = set()
    marker = None
    while True:
        params = {"Limit": 1000}
        if marker:
            params["Marker"] = marker
        page = kms.rpc("ListKeys", params)
        all_ids.update(k["KeyId"] for k in page.get("Keys", []))
        if not page.get("Truncated"):
            break
        marker = page.get("NextMarker")
        if not marker:
            break
    assert id1 in all_ids
    assert id2 in all_ids