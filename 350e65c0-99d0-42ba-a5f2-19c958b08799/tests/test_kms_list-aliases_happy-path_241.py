def test_list_aliases_filtered_by_key_id(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]

    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex[:12]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases", "--key-id", key_id)
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    aliases = parsed["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names
    for a in aliases:
        assert a.get("TargetKeyId") == key_id

    # Independent state read
    listed = kms.rpc("ListAliases", {"KeyId": key_id})["Aliases"]
    assert alias_name in [a["AliasName"] for a in listed]