def test_list_aliases_shows_created_alias(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    aliases = parsed["Aliases"]
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert matching, f"{alias_name} not found in list-aliases output"
    assert matching[0].get("TargetKeyId") == key_id

    # cross-check via independent read
    server_aliases = kms.rpc("ListAliases", {})["Aliases"]
    server_matching = [a for a in server_aliases if a["AliasName"] == alias_name]
    assert server_matching
    assert server_matching[0].get("TargetKeyId") == key_id