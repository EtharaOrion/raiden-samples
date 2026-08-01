def test_list_aliases_returns_seeded_alias(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/test-list-aliases-happy"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    aliases = payload["Aliases"]
    match = [a for a in aliases if a.get("AliasName") == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id

    server_aliases = kms.rpc("ListAliases", {})["Aliases"]
    server_match = [a for a in server_aliases if a.get("AliasName") == alias_name]
    assert len(server_match) == 1
    assert server_match[0].get("TargetKeyId") == key_id