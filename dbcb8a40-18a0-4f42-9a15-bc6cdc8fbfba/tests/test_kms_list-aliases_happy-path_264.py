def test_list_aliases_filtered_by_key_id(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {"Description": "list-aliases-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    import uuid
    alias_name = "alias/test-" + uuid.uuid4().hex

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases", "--key-id", key_id, "--limit", "100")
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    aliases = out["Aliases"]
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(matching) == 1
    assert matching[0]["TargetKeyId"] == key_id

    # independent read-back via kms
    listed = kms.rpc("ListAliases", {"KeyId": key_id})
    names = [a["AliasName"] for a in listed["Aliases"]]
    assert alias_name in names
    for a in listed["Aliases"]:
        assert a["TargetKeyId"] == key_id