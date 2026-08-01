def test_list_keys_marker_pagination(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "list-keys-marker-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    first = cli("kms", "list-keys", "--limit", "1")
    assert first.returncode == 0
    import json
    first_data = json.loads(first.stdout)
    assert "Keys" in first_data

    marker = first_data.get("NextMarker")
    if marker:
        result = cli("kms", "list-keys", "--marker", marker)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "Keys" in data
        assert isinstance(data["Keys"], list)

    all_ids = set()
    marker = None
    while True:
        payload = {}
        if marker:
            payload["Marker"] = marker
        page = kms.rpc("ListKeys", payload)
        for k in page.get("Keys", []):
            all_ids.add(k["KeyId"])
        if page.get("Truncated") and page.get("NextMarker"):
            marker = page["NextMarker"]
        else:
            break
    assert key_id in all_ids