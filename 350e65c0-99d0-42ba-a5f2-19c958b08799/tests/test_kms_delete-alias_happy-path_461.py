def test_delete_alias_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/delete-me-v22"

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert any(a["AliasName"] == alias_name for a in aliases_before)

    result = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert not any(a["AliasName"] == alias_name for a in aliases_after)

    # underlying key still exists
    md = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert md["KeyId"] == key_id