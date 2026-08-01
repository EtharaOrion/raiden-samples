def test_delete_alias_happy_path(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/delete-alias-happy-12"

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(a["AliasName"] == alias_name for a in aliases)

    result = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert not any(a["AliasName"] == alias_name for a in aliases_after)