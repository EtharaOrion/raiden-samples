def test_generate_mac_hmac_sha512_boundary_message(cli, kms, tmp_path):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_512",
            "Description": "generate-mac HMAC_SHA_512 test key",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = bytes(range(256)) * 16
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
        "HMAC_SHA_512",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["MacAlgorithm"] == "HMAC_SHA_512"
    assert isinstance(output["Mac"], str)
    assert base64.b64decode(output["Mac"], validate=True)

    verified = kms.rpc(
        "VerifyMac",
        {
            "KeyId": key_id,
            "Message": base64.b64encode(message).decode("ascii"),
            "Mac": output["Mac"],
            "MacAlgorithm": "HMAC_SHA_512",
        },
    )
    assert verified["MacValid"] is True
    assert verified["MacAlgorithm"] == "HMAC_SHA_512"