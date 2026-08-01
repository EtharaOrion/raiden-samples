def test_decrypt_symmetric_default_roundtrip(cli, kms, tmp_path):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "decrypt-edge"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload-1234"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_b64,
        "--encryption-algorithm", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext
    assert key_id in out["KeyId"]

    # Independent state assertion: decrypting via kms yields original plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext