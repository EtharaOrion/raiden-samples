def test_verify_mac_missing_required_message(cli, kms):
    import base64

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "verify-mac missing-message test",
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    message = base64.b64encode(b"message to authenticate").decode("ascii")

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
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_256",
        "--mac",
        generated["Mac"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "--message" in result.stderr
    assert "required" in result.stderr.lower()

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyUsage"] == "GENERATE_VERIFY_MAC"

    verification = kms.rpc(
        "VerifyMac",
        {
            "KeyId": key_id,
            "Message": message,
            "Mac": generated["Mac"],
            "MacAlgorithm": "HMAC_SHA_256",
        },
    )
    assert verification["MacValid"] is True