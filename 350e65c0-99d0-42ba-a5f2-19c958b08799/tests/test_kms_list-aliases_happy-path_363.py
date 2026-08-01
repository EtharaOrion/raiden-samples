def test_list_aliases_happy_path(cli, kms):
    key_id = kms.rpc("CreateKey", {})["KeyMetadata"]["KeyId"]
    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    data = json.loads(result.stdout)
    aliases = data["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(match) == 1
    assert match[0]["TargetKeyId"] == key_id

    # confirm via independent read
    listed = kms.rpc("ListAliases", {})["Aliases"]
    server_match = [a for a in listed if a["AliasName"] == alias_name]
    assert len(server_match) == 1
    assert server_match[0]["TargetKeyId"] == key_id