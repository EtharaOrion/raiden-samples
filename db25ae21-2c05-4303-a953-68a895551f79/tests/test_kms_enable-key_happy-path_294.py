def test_enable_key_restores_enabled_state(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {})
    key_id = created["KeyMetadata"]["KeyId"]

    # Prerequisite: disable the key first
    kms.rpc("DisableKey", {"KeyId": key_id})
    disabled = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert disabled["KeyMetadata"]["Enabled"] is False

    # Command under test
    result = cli("kms", "enable-key", "--key-id", key_id)
    assert result.returncode == 0

    # Assert resulting state via independent read
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True
    assert described["KeyMetadata"]["KeyState"] == "Enabled"

    # Enabled key can now perform crypto operations (round trip)
    import base64
    plaintext = b"hello enable"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext