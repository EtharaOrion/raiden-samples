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
    match = [a for a in aliases if a.get("AliasName") == alias_name]
    assert match, f"{alias_name} not in list-aliases output"
    assert match[0].get("TargetKeyId") == key_id

    # Independent read-back via kms
    listed = kms.rpc("ListAliases", {})["Aliases"]
    server_match = [a for a in listed if a.get("AliasName") == alias_name]
    assert server_match
    assert server_match[0].get("TargetKeyId") == key_id