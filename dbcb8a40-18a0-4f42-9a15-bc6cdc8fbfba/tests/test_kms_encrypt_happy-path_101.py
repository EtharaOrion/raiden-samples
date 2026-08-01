def test_encrypt_roundtrip_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    import base64
    plaintext = b"sensitive-data-1234"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext_b64)
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]

    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    decrypted = base64.b64decode(decrypt["Plaintext"])
    assert decrypted == plaintext