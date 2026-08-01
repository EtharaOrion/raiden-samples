def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-secret-value"
    b64_plaintext = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", b64_plaintext)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext = out["CiphertextBlob"]

    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or decrypted["KeyId"] == key_id