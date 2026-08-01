def test_generate_mac_hmac_sha_224_success(cli, kms, tmp_path):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_224",
            "Description": "generate-mac HMAC_SHA_224 test key",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = b"edge-case message for HMAC-SHA-224"
    message_file = tmp_path / "message.bin"
    message_file.write_bytes(message)

    result = cli(
        "kms",
        "generate-mac",
        "--message",
        f"fileb://{message_file}",
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_224",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["MacAlgorithm"] == "HMAC_SHA_224"
    assert isinstance(output["Mac"], str)
    assert output["Mac"]

    verification = kms.rpc(
        "VerifyMac",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "Mac": output["Mac"],
            "MacAlgorithm": "HMAC_SHA_224",
        },
    )
    assert verification["MacValid"] is True
    assert verification["MacAlgorithm"] == "HMAC_SHA_224"