def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import base64, json

    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-database-password-42"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_b64 = out["CiphertextBlob"]

    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or decrypted["KeyId"] == key_id