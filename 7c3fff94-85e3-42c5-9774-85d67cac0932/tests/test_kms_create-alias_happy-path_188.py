def test_create_alias_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "create-alias happy path"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/create-alias-{key_id}"

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