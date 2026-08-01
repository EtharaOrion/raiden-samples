def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-database-password"
    b64_plaintext = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", b64_plaintext)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]
    assert isinstance(ciphertext_blob, str) and ciphertext_blob

    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id