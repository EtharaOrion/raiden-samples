def test_generate_mac_missing_required_message(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "HMAC key for missing message validation",
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert before["Enabled"] is True

    result = cli(
        "kms",
        "generate-mac",
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--message" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert after["Enabled"] is True
    assert after["KeyState"] == before["KeyState"]