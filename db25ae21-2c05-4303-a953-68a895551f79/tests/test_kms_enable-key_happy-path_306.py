def test_enable_key_happy_path(cli, kms):
    key_id = kms.rpc("CreateKey", {})["KeyMetadata"]["KeyId"]
    kms.rpc("DisableKey", {"KeyId": key_id})
    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["Enabled"] is False

    result = cli("kms", "enable-key", "--key-id", key_id)
    assert result.returncode == 0

    meta = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"

    import base64
    pt = base64.b64encode(b"round-trip-data").decode()
    ct = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt})["CiphertextBlob"]
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ct})["Plaintext"]
    assert dec == pt