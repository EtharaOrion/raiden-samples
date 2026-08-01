def test_create_key_happy_path(cli, kms, tmp_path):
    import json

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

    # Read back the resulting state independently
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    meta = described["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Description"] == "my test key"
    assert meta["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"

    # Verify usability via an encrypt->decrypt round trip
    import base64
    plaintext = b"hello world"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext