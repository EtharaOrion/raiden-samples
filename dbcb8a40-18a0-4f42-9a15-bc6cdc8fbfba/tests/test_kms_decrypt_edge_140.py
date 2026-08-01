def test_decrypt_asymmetric_roundtrip(cli, kms):
    import json, base64

    create = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-edge-data"
    b64_plain = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": b64_plain,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
        "--key-id", key_id,
        "--encryption-algorithm", "RSAES_OAEP_SHA_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent read-back via kms client
    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext_blob,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext