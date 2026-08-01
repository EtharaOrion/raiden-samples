def test_delete_alias_happy_path(cli, kms):
    import uuid

    alias_name = f"alias/delete-alias-{uuid.uuid4().hex}"
    key = kms.rpc("CreateKey", {"Description": "delete-alias happy-path test"})
    key_id = key["KeyMetadata"]["KeyId"]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    before = kms.rpc("ListAliases", {})
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in before["Aliases"]
    )

    result = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert result.returncode == 0

    after = kms.rpc("ListAliases", {})
    assert all(alias.get("AliasName") != alias_name for alias in after["Aliases"])

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id