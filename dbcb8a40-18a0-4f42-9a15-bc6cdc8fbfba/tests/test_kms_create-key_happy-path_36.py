def test_create_key_happy_path(cli, kms):
    import json

    result = cli(
        "kms", "create-key",
        "--description", "my test key",
        "--key-usage", "ENCRYPT_DECRYPT",
        "--key-spec", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    key_id = out["KeyMetadata"]["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    meta = described["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Description"] == "my test key"
    assert meta["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"

    import base64
    plaintext = b"round-trip-data"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext