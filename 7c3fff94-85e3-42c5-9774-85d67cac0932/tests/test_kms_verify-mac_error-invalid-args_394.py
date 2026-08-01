def test_verify_mac_missing_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"KeyUsage": "GENERATE_VERIFY_MAC", "KeySpec": "HMAC_256"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    message = "dmVyaWZ5LW1hYy1taXNzaW5nLWtleS1pZA=="

    generated = kms.rpc(
        "GenerateMac",
        {
            "KeyId": key_id,
            "Message": message,
            "MacAlgorithm": "HMAC_SHA_256",
        },
    )

    result = cli(
        "kms",
        "verify-mac",
        "--message",
        message,
        "--mac-algorithm",
        "HMAC_SHA_256",
        "--mac",
        generated["Mac"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert metadata["Enabled"] is True