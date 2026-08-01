def test_delete_alias_happy_path(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/test-delete-alias-happy"

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    before = kms.rpc("ListAliases", {})
    assert any(a["AliasName"] == alias_name for a in before["Aliases"])

    result = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert result.returncode == 0

    after = kms.rpc("ListAliases", {})
    assert not any(a["AliasName"] == alias_name for a in after["Aliases"])