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
    assert match, f"{alias_name} not found in list-aliases output"
    assert match[0].get("TargetKeyId") == key_id

    # independent read-back via kms
    listed = kms.rpc("ListAliases", {})["Aliases"]
    match2 = [a for a in listed if a["AliasName"] == alias_name]
    assert match2
    assert match2[0].get("TargetKeyId") == key_id