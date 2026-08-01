def test_verify_mac_happy_path_verifies_generated_mac(cli, kms):
    import base64
    import json
    import uuid

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "verify-mac-happy-" + uuid.uuid4().hex,
            "KeyUsage": "GENERATE_VERIFY_MAC",
            "KeySpec": "HMAC_256",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    message = base64.b64encode(b"verify-mac happy path message").decode("ascii")

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
        "--message",
        message,
        "--mac-algorithm",
        "HMAC_SHA_256",
        "--mac",
        generated["Mac"],
    )
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert output["MacValid"] is True
