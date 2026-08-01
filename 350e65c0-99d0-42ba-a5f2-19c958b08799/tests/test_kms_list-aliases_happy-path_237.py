def test_list_aliases_happy_path(cli, kms):
    key_id = kms.rpc("CreateKey", {"Description": "list-aliases-test"})["KeyMetadata"]["KeyId"]
    alias_name = "alias/list-aliases-happy-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    aliases = parsed["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    matched = [a for a in aliases if a["AliasName"] == alias_name]
    assert any(a.get("TargetKeyId") == key_id for a in matched)

    # cross-check via independent read of kms state
    listed = kms.rpc("ListAliases", {})["Aliases"]
    state_names = [a["AliasName"] for a in listed]
    assert alias_name in state_names
    state_matched = [a for a in listed if a["AliasName"] == alias_name]
    assert any(a.get("TargetKeyId") == key_id for a in state_matched)