def test_create_key_happy_path(cli, kms):
    import json
    import base64

    result = cli(
        "kms", "create-key",
        "--description", "happy-path-key",
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
    assert meta["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert meta["Enabled"] is True

    plaintext = b"round-trip-secret"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext