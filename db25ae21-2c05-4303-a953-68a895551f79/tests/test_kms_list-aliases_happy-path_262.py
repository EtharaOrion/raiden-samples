def test_list_aliases_with_limit_and_marker(cli, kms):
    # Seed prerequisite state: create a key and an alias
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex[:12]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    # First page with a limit of 1 to obtain a marker
    first = cli("kms", "list-aliases", "--limit", "1")
    assert first.returncode == 0

    import json
    first_data = json.loads(first.stdout)
    assert "Aliases" in first_data

    marker = first_data.get("NextMarker")

    if marker:
        # Second page using the returned marker
        second = cli("kms", "list-aliases", "--limit", "50", "--marker", marker)
        assert second.returncode == 0
        second_data = json.loads(second.stdout)
        assert "Aliases" in second_data

    # Assert resulting state via independent read: our alias exists
    listed = kms.rpc("ListAliases", {})
    names = {a["AliasName"] for a in listed["Aliases"]}
    assert alias_name in names

    match = [a for a in listed["Aliases"] if a["AliasName"] == alias_name]
    assert match[0].get("TargetKeyId") == key_id