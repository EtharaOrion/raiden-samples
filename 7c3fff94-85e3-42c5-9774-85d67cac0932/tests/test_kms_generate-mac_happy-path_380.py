def test_generate_mac_happy_path(cli, kms):
    import base64
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "HMAC key for generate-mac test",
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    message = base64.b64encode(b"message authenticated by KMS").decode("ascii")
    result = cli(
        "kms",
        "generate-mac",
        "--message",
        message,
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_256",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["KeyId"]
    assert output["MacAlgorithm"] == "HMAC_SHA_256"
    assert base64.b64decode(output["Mac"], validate=True)

    verified = kms.rpc(
        "VerifyMac",
        {
            "KeyId": key_id,
            "Message": message,
            "Mac": output["Mac"],
            "MacAlgorithm": "HMAC_SHA_256",
        },
    )
    assert verified["MacValid"] is True
    assert verified["MacAlgorithm"] == "HMAC_SHA_256"