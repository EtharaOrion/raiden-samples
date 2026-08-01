def test_list_aliases_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/test-list-aliases-happy"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    aliases = parsed["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    entry = next(a for a in aliases if a["AliasName"] == alias_name)
    assert entry.get("TargetKeyId") == key_id

    listed = kms.rpc("ListAliases", {})
    state_names = [a["AliasName"] for a in listed["Aliases"]]
    assert alias_name in state_names