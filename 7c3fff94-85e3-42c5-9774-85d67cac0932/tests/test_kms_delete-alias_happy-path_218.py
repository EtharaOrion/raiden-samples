def test_delete_alias_happy_path(cli, kms, tmp_path):
    import uuid

    key = kms.rpc("CreateKey", {"Description": "delete-alias test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/delete-test-{uuid.uuid4().hex}"

    kms.rpc("CreateAlias", {
        "AliasName": alias_name,
        "TargetKeyId": key_id,
    })

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in aliases_before
    )

    result = cli(
        "kms",
        "delete-alias",
        "--alias-name",
        alias_name,
    )
    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias.get("AliasName") != alias_name for alias in aliases_after)

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id