def test_decrypt_invalid_ciphertext_blob(cli, kms):
    # Seed a valid key and produce a real ciphertext so we can corrupt it
    created = kms.rpc("CreateKey", {"Description": "decrypt-invalid-arg-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    import base64
    plaintext = base64.b64encode(b"hello world").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    valid_blob = enc["CiphertextBlob"]

    # Sanity: the valid blob round-trips
    dec = kms.rpc("Decrypt", {"CiphertextBlob": valid_blob})
    assert base64.b64decode(dec["Plaintext"]) == b"hello world"

    # Now attempt to decrypt an invalid/corrupted ciphertext blob
    garbage = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext-blob").decode()
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", garbage,
        "--grant-tokens", "xxxxxxxxxxx",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    # The seed key must still exist and be usable (round-trip intact)
    dec2 = kms.rpc("Decrypt", {"CiphertextBlob": valid_blob})
    assert base64.b64decode(dec2["Plaintext"]) == b"hello world"