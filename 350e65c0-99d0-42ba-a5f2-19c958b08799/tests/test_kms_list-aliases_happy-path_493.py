def test_list_aliases_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/test-list-aliases-happy-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    aliases = parsed["Aliases"]
    assert any(a["AliasName"] == alias_name for a in aliases)

    server_aliases = kms.rpc("ListAliases", {})["Aliases"]
    matching = [a for a in server_aliases if a["AliasName"] == alias_name]
    assert matching
    assert matching[0]["TargetKeyId"] == key_id