def test_decrypt_asymmetric_rsa_oaep_roundtrip(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": pt_b64,
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

    # independent read-back through raw kms client
    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext_blob,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext