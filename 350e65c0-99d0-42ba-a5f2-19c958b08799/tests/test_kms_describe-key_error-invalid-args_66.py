def test_describe_key_invalid_args(cli, kms):
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli("kms", "describe-key", "--key-id", key_id, "--not-a-real-flag", "x")

    assert result.returncode != 0
    assert "not-a-real-flag" in result.stderr or "Unknown" in result.stderr or "usage" in result.stderr.lower()

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id