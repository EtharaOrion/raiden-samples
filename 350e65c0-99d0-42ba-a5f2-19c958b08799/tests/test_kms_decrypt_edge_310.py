def test_decrypt_asymmetric_rsaes_oaep_sha1(cli, kms, tmp_path):
    import base64, json

    # Seed: create an asymmetric encryption KMS key
    created = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext with the matching algorithm
    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": pt_b64,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_1",
    })
    ciphertext_b64 = enc["CiphertextBlob"]

    # Decrypt via the CLI using the same encryption algorithm
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_b64,
        "--key-id", key_id,
        "--encryption-algorithm", "RSAES_OAEP_SHA_1",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    returned_pt = base64.b64decode(out["Plaintext"])
    assert returned_pt == plaintext

    # Independent read-back: decrypt the same blob directly via kms rpc
    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext_b64,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_1",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext