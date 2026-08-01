def test_enable_key_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "enable-key test"})
    key_id = create["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})
    disabled = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert disabled["KeyMetadata"]["Enabled"] is False

    result = cli("kms", "enable-key", "--key-id", key_id)
    assert result.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True
    assert described["KeyMetadata"]["KeyState"] == "Enabled"

    import base64
    plaintext = b"round-trip-check"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext