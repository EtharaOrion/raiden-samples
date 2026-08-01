def test_decrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import base64, json

    # Seed a KMS key
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to get a valid ciphertext blob
    plaintext = b"hello-decrypt-happy-path"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run decrypt under test
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Assert the decrypted plaintext matches the original (round trip)
    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent read-back via kms: decrypting the same blob returns the same plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext