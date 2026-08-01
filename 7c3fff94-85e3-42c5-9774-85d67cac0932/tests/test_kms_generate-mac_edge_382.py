def test_generate_mac_maximum_length_message(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "HMAC key for generate-mac edge test",
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = bytes(range(256)) * 16
    encoded_message = base64.b64encode(message).decode("ascii")

    result = cli(
        "kms",
        "generate-mac",
        "--message",
        encoded_message,
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["MacAlgorithm"] == "HMAC_SHA_256"
    assert isinstance(output["Mac"], str)
    assert base64.b64decode(output["Mac"], validate=True)

    verified = kms.rpc(
        "VerifyMac",
        {
            "KeyId": key_id,
            "Message": encoded_message,
            "Mac": output["Mac"],
            "MacAlgorithm": "HMAC_SHA_256",
        },
    )
    assert verified["MacValid"] is True
    assert verified["MacAlgorithm"] == "HMAC_SHA_256"