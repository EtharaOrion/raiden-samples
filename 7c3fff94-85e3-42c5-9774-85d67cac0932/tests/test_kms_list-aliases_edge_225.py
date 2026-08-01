def test_list_aliases_with_limit_one(cli, kms, tmp_path):
    import json

    created = kms.rpc(
        "CreateKey",
        {"Description": "key for list-aliases limit test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    alias_name = "alias/list-limit-" + key_id

    kms.rpc(
        "CreateAlias",
        {"AliasName": alias_name, "TargetKeyId": key_id},
    )

    result = cli("kms", "list-aliases", "--limit", "1")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output.get("Aliases"), list)
    assert output["Aliases"]

    aliases = kms.rpc("ListAliases", {"KeyId": key_id})
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in aliases["Aliases"]
    )