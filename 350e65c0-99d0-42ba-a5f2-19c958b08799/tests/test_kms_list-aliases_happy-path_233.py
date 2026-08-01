def test_list_aliases_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/test-list-aliases-happy"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    entry = next(a for a in aliases if a["AliasName"] == alias_name)
    assert entry.get("TargetKeyId") == key_id

    # independent read-back via raw RPC
    rpc_aliases = kms.rpc("ListAliases", {})["Aliases"]
    rpc_entry = next(a for a in rpc_aliases if a["AliasName"] == alias_name)
    assert rpc_entry.get("TargetKeyId") == key_id