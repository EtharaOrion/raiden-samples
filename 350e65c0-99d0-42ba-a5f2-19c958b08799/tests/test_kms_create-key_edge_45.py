def test_create_key_hmac_256_keyspec(cli, kms):
    result = cli("kms", "create-key", "--key-spec", "HMAC_256", "--key-usage", "GENERATE_VERIFY_MAC")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    key_id = payload["KeyMetadata"]["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    md = described["KeyMetadata"]
    assert md["KeyId"] == key_id
    assert md["KeySpec"] == "HMAC_256"
    assert md["KeyUsage"] == "GENERATE_VERIFY_MAC"

    import base64
    msg = base64.b64encode(b"hello mac").decode()
    gen = kms.rpc("GenerateMac", {"KeyId": key_id, "Message": msg, "MacAlgorithm": "HMAC_SHA_256"})
    verify = kms.rpc("VerifyMac", {
        "KeyId": key_id,
        "Message": msg,
        "Mac": gen["Mac"],
        "MacAlgorithm": "HMAC_SHA_256",
    })
    assert verify["MacValid"] is True