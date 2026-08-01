def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import base64, json

    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-database-password"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64
    assert base64.b64decode(ciphertext_b64) != plaintext

    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id