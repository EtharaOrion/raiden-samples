def test_list_aliases_filtered_by_key_id(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    alias_name = "alias/test-list-aliases-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases", "--key-id", key_id, "--limit", "50")
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    aliases = out["Aliases"]
    names = [a["AliasName"] for a in aliases]
    assert alias_name in names

    for a in aliases:
        if a["AliasName"] == alias_name:
            assert a.get("TargetKeyId") == key_id

    # Independent read back through kms confirms the alias/key association
    described = kms.rpc("ListAliases", {"KeyId": key_id})
    described_names = [a["AliasName"] for a in described["Aliases"]]
    assert alias_name in described_names