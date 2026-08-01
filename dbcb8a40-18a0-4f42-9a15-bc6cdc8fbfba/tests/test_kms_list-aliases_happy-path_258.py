def test_list_aliases_returns_created_alias(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]
    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    # confirm via independent read
    state = kms.rpc("ListAliases", {})
    state_names = [a["AliasName"] for a in state["Aliases"]]
    assert alias_name in state_names
    matched = [a for a in state["Aliases"] if a["AliasName"] == alias_name][0]
    assert matched["TargetKeyId"] == key_id