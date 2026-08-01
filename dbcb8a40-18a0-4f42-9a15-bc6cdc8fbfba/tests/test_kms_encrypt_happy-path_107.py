def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-value"
    b64_plain = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", b64_plain)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext = out["CiphertextBlob"]
    assert ciphertext

    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    decrypted = base64.b64decode(decrypt["Plaintext"])
    assert decrypted == plaintext