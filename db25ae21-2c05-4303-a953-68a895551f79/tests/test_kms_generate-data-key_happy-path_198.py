def test_generate_data_key_happy_path(cli, kms, tmp_path):
    import json
    import base64

    # Seed a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run the command under test
    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert "KeyId" in out

    # Plaintext should be a 256-bit (32 byte) key
    plaintext_bytes = base64.b64decode(out["Plaintext"])
    assert len(plaintext_bytes) == 32

    # The CiphertextBlob must decrypt back to the same plaintext via the seeded key
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext_bytes

    # Confirm the returned KeyId resolves to our seeded key
    describe = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert describe["KeyMetadata"]["KeyId"] == key_id