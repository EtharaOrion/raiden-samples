def test_list_aliases_with_limit_and_marker(cli, kms):
    # Seed prerequisite state: create a key and an alias
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    # First page with a limit of 1 to obtain a marker if truncated
    first = cli("kms", "list-aliases", "--limit", "1")
    assert first.returncode == 0
    import json
    first_payload = json.loads(first.stdout)
    assert "Aliases" in first_payload

    # If truncated, use the marker to page through
    marker = first_payload.get("NextMarker")
    if marker:
        second = cli("kms", "list-aliases", "--limit", "1", "--marker", marker)
        assert second.returncode == 0
        second_payload = json.loads(second.stdout)
        assert "Aliases" in second_payload

    # Independent read: the seeded alias must be present in the full listing
    listed = kms.rpc("ListAliases", {})
    names = [a["AliasName"] for a in listed["Aliases"]]
    assert alias_name in names
    for a in listed["Aliases"]:
        if a["AliasName"] == alias_name:
            assert a.get("TargetKeyId") == key_id
            break