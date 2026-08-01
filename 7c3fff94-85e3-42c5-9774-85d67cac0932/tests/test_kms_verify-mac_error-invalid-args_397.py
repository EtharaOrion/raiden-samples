def test_verify_mac_missing_mac_algorithm(cli, kms, tmp_path):
    import base64

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "verify-mac missing algorithm test",
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = b"message authenticated by the test key"
    generated = kms.rpc(
        "GenerateMac",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "MacAlgorithm": "HMAC_SHA_256",
        },
    )

    message_path = tmp_path / "message.bin"
    mac_path = tmp_path / "mac.bin"
    message_path.write_bytes(message)
    mac_path.write_bytes(base64.b64decode(generated["Mac"]))

    result = cli(
        "kms",
        "verify-mac",
        "--message",
        f"fileb://{message_path}",
        "--key-id",
        key_id,
        "--mac",
        f"fileb://{mac_path}",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--mac-algorithm" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert metadata["KeySpec"] == "HMAC_256"
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"