def test_generate_mac_requires_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "generate-mac missing key-id test",
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert before["KeySpec"] == "HMAC_256"
    assert before["Enabled"] is True

    result = cli(
        "kms",
        "generate-mac",
        "--message",
        "dGVzdA==",
        "--mac-algorithm",
        "HMAC_SHA_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "key-id" in result.stderr.lower()

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyUsage"] == before["KeyUsage"]
    assert after["KeySpec"] == before["KeySpec"]
    assert after["Enabled"] == before["Enabled"]
    assert after["KeyState"] == before["KeyState"]