def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-password-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Verify the round trip: decrypt the produced ciphertext independently
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    decrypted = base64.b64decode(dec["Plaintext"])
    assert decrypted == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id