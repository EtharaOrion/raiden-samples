def test_create_key_happy_path(cli, kms, tmp_path):
    import json, base64

    result = cli(
        "kms", "create-key",
        "--description", "my test key",
        "--key-usage", "ENCRYPT_DECRYPT",
        "--key-spec", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)
    key_meta = payload["KeyMetadata"]
    key_id = key_meta["KeyId"]
    assert key_id

    # Read back state independently
    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["Description"] == "my test key"
    assert described["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert described["Enabled"] is True
    assert described["KeyState"] == "Enabled"

    # Verify the key actually works via an encrypt->decrypt round trip
    plaintext = b"round-trip-check"
    b64_plain = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": b64_plain})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext