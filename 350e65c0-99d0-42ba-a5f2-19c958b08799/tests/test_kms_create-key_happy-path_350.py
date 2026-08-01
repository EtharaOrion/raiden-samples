def test_create_key_happy_path(cli, kms):
    result = cli("kms", "create-key", "--description", "my test key")
    assert result.returncode == 0, result.stderr

    import json
    payload = json.loads(result.stdout)
    key_id = payload["KeyMetadata"]["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    meta = described["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Description"] == "my test key"
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"

    # verify the key works for encryption round-trip
    import base64
    plaintext = b"hello world"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext