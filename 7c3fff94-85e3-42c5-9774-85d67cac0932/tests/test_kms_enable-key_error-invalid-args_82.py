def test_enable_key_rejects_unknown_flag_without_enabling_key(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid enable-key arguments test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "Disabled"
    assert before["Enabled"] is False

    result = cli(
        "kms",
        "enable-key",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyState"] == "Disabled"
    assert after["Enabled"] is False