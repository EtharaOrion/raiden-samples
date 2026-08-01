def test_generate_mac_rejects_unknown_flag(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-mac invalid-argument test",
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert before["KeyState"] == "Enabled"
    assert before["Enabled"] is True

    result = cli(
        "kms",
        "generate-mac",
        "--message",
        "dGVzdC1tZXNzYWdl",
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_256",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert after["KeySpec"] == "HMAC_256"
    assert after["KeyState"] == "Enabled"
    assert after["Enabled"] is True