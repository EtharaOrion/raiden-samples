def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Prerequisite: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-password-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Independent read: decrypt the ciphertext and assert round-trip
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert key_id in decrypt["KeyId"]