def test_generate_mac_hmac_sha_384(cli, kms):
    import base64
    import json

    key = kms.rpc(
        "CreateKey",
        {
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_384",
            "Description": "generate-mac HMAC-SHA-384 test key",
        },
    )
    key_id = key["KeyMetadata"]["KeyId"]

    message = b"edge-case message for HMAC-SHA-384"
    encoded_message = base64.b64encode(message).decode("ascii")

    result = cli(
        "kms",
        "generate-mac",
        "--message",
        encoded_message,
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_384",
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["MacAlgorithm"] == "HMAC_SHA_384"
    assert base64.b64decode(output["Mac"], validate=True)

    verification = kms.rpc(
        "VerifyMac",
        {
            "KeyId": key_id,
            "Message": encoded_message,
            "Mac": output["Mac"],
            "MacAlgorithm": "HMAC_SHA_384",
        },
    )
    assert verification["MacValid"] is True
    assert verification["MacAlgorithm"] == "HMAC_SHA_384"