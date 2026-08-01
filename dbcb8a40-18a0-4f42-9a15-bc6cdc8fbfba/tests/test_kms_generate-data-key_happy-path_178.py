def test_generate_data_key_happy_path(cli, kms, tmp_path):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "gdk-test", "KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert "KeyId" in out

    # Plaintext must be valid base64 and 32 bytes for AES_256
    plaintext_bytes = base64.b64decode(out["Plaintext"])
    assert len(plaintext_bytes) == 32

    # Verify the returned KeyId resolves to the key we created
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Verify the encrypted data key round-trips through KMS Decrypt back to the plaintext
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert decrypt["Plaintext"] == out["Plaintext"]
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext_bytes