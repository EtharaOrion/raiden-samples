def test_create_key_happy_path(cli, kms):
    result = cli("kms", "create-key", "--description", "my-test-key")
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    key_id = out["KeyMetadata"]["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    meta = described["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Description"] == "my-test-key"
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"

    # verify encrypt->decrypt round trip
    import base64
    plaintext = b"round-trip-secret"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext