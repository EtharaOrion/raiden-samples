def test_create_key_happy_path(cli, kms):
    import json, base64

    result = cli(
        "kms", "create-key",
        "--description", "black-box happy path key",
        "--key-spec", "SYMMETRIC_DEFAULT",
        "--key-usage", "ENCRYPT_DECRYPT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    meta = out["KeyMetadata"]
    key_id = meta["KeyId"]
    assert key_id

    # Independent read-back of resulting state
    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["Description"] == "black-box happy path key"
    assert described["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert described["Enabled"] is True
    assert described["KeyState"] == "Enabled"

    # Verify the key is usable via an Encrypt->Decrypt round trip
    plaintext = b"hello kms happy path"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext