def test_decrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import base64, json

    # Seed a KMS key
    key = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    # Encrypt some plaintext via the backend to obtain a ciphertext blob
    plaintext = b"hello-decrypt-world"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test: decrypt the ciphertext blob
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # The decrypted Plaintext must round-trip to the original input
    assert base64.b64decode(out["Plaintext"]) == plaintext
    # And it must be attributed to the seeded key
    assert out["KeyId"].endswith(key_id) or key_id in out["KeyId"]

    # Independent read-back: backend Decrypt yields the same plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert key_id in dec["KeyId"]