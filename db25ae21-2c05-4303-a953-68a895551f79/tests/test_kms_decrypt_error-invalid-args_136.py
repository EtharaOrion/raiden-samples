def test_decrypt_invalid_args(cli, kms):
    # Seed valid state so the only problem is the unknown flag
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]
    import base64
    plaintext = base64.b64encode(b"secret-data").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    blob = enc["CiphertextBlob"]

    # Run decrypt with a bogus flag -> must fail to parse
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", blob,
        "--not-a-real-flag", "x",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown" in result.stderr or "unrecognized" in result.stderr.lower()

    # State unchanged: the key still decrypts correctly via a valid call
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob})
    assert dec["Plaintext"] == plaintext