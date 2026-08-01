def test_describe_key_invalid_args_unknown_flag(cli, kms):
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "describe-key",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert "attribute-definitions" in result.stderr.lower() or "unknown" in result.stderr.lower() or "usage" in result.stderr.lower()

    # Key state should be unaffected
    describe = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert describe["KeyMetadata"]["KeyId"] == key_id
    assert describe["KeyMetadata"]["KeyState"] == "Enabled"