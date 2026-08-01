def test_create_alias_associates_alias_with_target_key(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "create-alias happy path target"})
    key_id = created["KeyMetadata"]["KeyId"]
    alias_name = f"alias/pytest-create-alias-{key_id}"

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        key_id,
    )

    assert result.returncode == 0, result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == key_id