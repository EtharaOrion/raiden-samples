def test_decrypt_roundtrip_happy_path(cli, kms):
    import json, base64

    # Seed a symmetric key
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt some plaintext to produce a ciphertext blob
    plaintext = b"hello decrypt roundtrip"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test: decrypt the ciphertext blob
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # The decrypted plaintext must match the original input
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent read: decrypt via kms rpc to confirm the ciphertext is valid state
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or key_id in dec["KeyId"]