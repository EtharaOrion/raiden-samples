def test_enable_key_invalid_args(cli, kms):
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})

    result = cli("kms", "enable-key", "--key-id", key_id, "--not-a-real-flag", "x")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is False