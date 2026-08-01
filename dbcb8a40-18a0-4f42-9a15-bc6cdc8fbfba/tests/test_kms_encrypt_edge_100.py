def test_encrypt_asymmetric_rsa_oaep_roundtrip(cli, kms, tmp_path):
    import json, base64

    created = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    plaintext = b"secret-payload-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--encryption-algorithm", "RSAES_OAEP_SHA_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    dec = kms.rpc("Decrypt", {
        "KeyId": key_id,
        "CiphertextBlob": ciphertext_b64,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext