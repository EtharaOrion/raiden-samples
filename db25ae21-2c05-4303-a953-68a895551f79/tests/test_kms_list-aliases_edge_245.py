def test_list_aliases_filtered_by_key_id(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]

    alias_name = "alias/test-list-alias-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases", "--key-id", key_id)
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names
    for a in aliases:
        if a["AliasName"] == alias_name:
            assert a.get("TargetKeyId") == key_id

    # independent read-back through kms
    state = kms.rpc("ListAliases", {"KeyId": key_id})
    state_names = [a["AliasName"] for a in state["Aliases"]]
    assert alias_name in state_names