def test_create_key_customer_master_key_spec_symmetric(cli, kms):
    result = cli("kms", "create-key", "--customer-master-key-spec", "SYMMETRIC_DEFAULT")
    assert result.returncode == 0, result.stderr

    import json
    payload = json.loads(result.stdout)
    key_id = payload["KeyMetadata"]["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    meta = described["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"
    assert meta["KeyUsage"] == "ENCRYPT_DECRYPT"

    # verify the key is functional via an encrypt->decrypt round trip
    import base64
    plaintext = b"round-trip-check"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext