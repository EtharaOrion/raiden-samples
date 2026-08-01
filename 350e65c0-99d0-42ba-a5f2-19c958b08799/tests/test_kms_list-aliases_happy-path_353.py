def test_list_aliases_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/test-list-aliases-happy-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    # confirm the same via an independent read
    state = kms.rpc("ListAliases", {})
    state_names = [a["AliasName"] for a in state["Aliases"]]
    assert alias_name in state_names
    entry = next(a for a in state["Aliases"] if a["AliasName"] == alias_name)
    assert entry["TargetKeyId"] == key_id