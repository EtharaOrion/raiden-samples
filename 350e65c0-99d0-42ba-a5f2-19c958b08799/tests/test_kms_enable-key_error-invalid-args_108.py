def test_enable_key_invalid_args(cli, kms):
    # Seed a real, disabled key so the command target exists but the unknown flag is fatal.
    create = kms.rpc("CreateKey", {"Description": "invalid-args-test"})
    key_id = create["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})

    # Sanity: key is disabled before the (rejected) command runs.
    before = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert before["KeyMetadata"]["Enabled"] is False

    result = cli(
        "kms", "enable-key",
        "--key-id", key_id,
        "--not-a-real-flag", "x",
    )

    # Unknown flag -> non-zero exit and an argument-parse error category in stderr.
    assert result.returncode != 0
    assert "not-a-real-flag" in result.stderr or "Unknown" in result.stderr or "usage" in result.stderr.lower()

    # State unchanged: the invalid invocation must NOT have enabled the key.
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["Enabled"] is False