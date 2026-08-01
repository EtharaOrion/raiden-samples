def test_list_aliases_rejects_zero_limit(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "list-aliases invalid limit test"})
    key_id = created["KeyMetadata"]["KeyId"]
    alias_name = f"alias/list-aliases-limit-zero-{key_id}"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "list-aliases", "--limit", "0")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias["AliasName"] == alias_name and alias.get("TargetKeyId") == key_id
        for alias in aliases
    )