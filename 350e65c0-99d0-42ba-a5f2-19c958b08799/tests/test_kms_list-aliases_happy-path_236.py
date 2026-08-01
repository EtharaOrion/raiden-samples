def test_list_aliases_shows_created_alias(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "list-aliases-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/list-aliases-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    assert "Aliases" in parsed
    names = [a["AliasName"] for a in parsed["Aliases"]]
    assert alias_name in names

    matching = [a for a in parsed["Aliases"] if a["AliasName"] == alias_name]
    assert matching
    assert matching[0].get("TargetKeyId") == key_id

    # cross-check via independent read
    listed = kms.rpc("ListAliases", {})
    server_names = [a["AliasName"] for a in listed["Aliases"]]
    assert alias_name in server_names