def test_delete_alias_nonexistent(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "delete-alias nonexistent test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/delete-alias-nonexistent-" + key_id

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})
    kms.rpc("DeleteAlias", {"AliasName": alias_name})

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias["AliasName"] != alias_name for alias in aliases_before)

    result = cli("kms", "delete-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias["AliasName"] != alias_name for alias in aliases_after)
    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["KeyId"] == key_id