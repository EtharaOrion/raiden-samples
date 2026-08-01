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
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(matching) == 1
    assert matching[0].get("TargetKeyId") == key_id

    # independent read-back via kms
    listed = kms.rpc("ListAliases", {})
    names = [a["AliasName"] for a in listed["Aliases"]]
    assert alias_name in names