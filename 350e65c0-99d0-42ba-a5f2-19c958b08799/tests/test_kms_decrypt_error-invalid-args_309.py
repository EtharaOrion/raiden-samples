def test_decrypt_invalid_flag_rejected(cli, kms):
    # Seed real state: create a key and produce a valid ciphertext blob
    create = kms.rpc("CreateKey", {"Description": "decrypt-invalid-flag"})
    key_id = create["KeyMetadata"]["KeyId"]
    import base64
    plaintext = b"hello-world"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    blob = enc["CiphertextBlob"]

    # Run command under test with a bogus flag -> must be rejected
    result = cli("kms", "decrypt", "--ciphertext-blob", blob, "--not-a-real-flag", "x")
    assert result.returncode != 0
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # The valid ciphertext still decrypts correctly via a proper call (state intact)
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext