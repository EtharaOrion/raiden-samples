def test_generate_mac_happy_path(cli, kms, tmp_path):
    import base64
    import json

    key = kms.rpc(
        "CreateKey",
        {
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
            "Description": "generate-mac happy-path test key",
        },
    )
    key_id = key["KeyMetadata"]["KeyId"]

    message = b"message authenticated by KMS"
    message_path = tmp_path / "message.bin"
    message_path.write_bytes(message)

    result = cli(
        "kms",
        "generate-mac",
        "--message",
        f"fileb://{message_path}",
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["MacAlgorithm"] == "HMAC_SHA_256"
    assert isinstance(output["Mac"], str)
    assert output["Mac"]

    verification = kms.rpc(
        "VerifyMac",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "Mac": output["Mac"],
            "MacAlgorithm": "HMAC_SHA_256",
        },
    )
    assert verification["MacValid"] is True
    assert verification["MacAlgorithm"] == "HMAC_SHA_256"