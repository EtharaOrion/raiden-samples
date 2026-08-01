def test_decrypt_asymmetric_rsa_oaep_roundtrip(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": plaintext_b64,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    ciphertext_b64 = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_b64,
        "--key-id", key_id,
        "--encryption-algorithm", "RSAES_OAEP_SHA_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # independent read-back verification via kms
    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext_b64,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext