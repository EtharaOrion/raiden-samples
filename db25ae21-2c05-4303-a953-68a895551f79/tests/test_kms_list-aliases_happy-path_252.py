def test_list_aliases_shows_created_alias(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]
    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    aliases = parsed["Aliases"]
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(matching) == 1
    assert matching[0]["TargetKeyId"] == key_id

    # Independent read-back via kms to confirm state
    listed = kms.rpc("ListAliases", {})
    names = [a["AliasName"] for a in listed["Aliases"]]
    assert alias_name in names