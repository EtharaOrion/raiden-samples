def test_list_aliases_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "list-aliases-test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/list-aliases-happy-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    assert "Aliases" in parsed
    names = [a["AliasName"] for a in parsed["Aliases"]]
    assert alias_name in names

    listed = kms.rpc("ListAliases", {})
    seeded = [a for a in listed["Aliases"] if a["AliasName"] == alias_name]
    assert len(seeded) == 1
    assert seeded[0].get("TargetKeyId") == key_id