def test_kms_decrypt_invalid_ciphertext_blob(cli, kms):
    # Seed a valid key and produce a real ciphertext so the environment is functional.
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    import base64
    plaintext = base64.b64encode(b"hello world").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    valid_blob = enc["CiphertextBlob"]

    # Sanity: the valid ciphertext round-trips.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": valid_blob})
    assert base64.b64decode(dec["Plaintext"]) == b"hello world"

    # Now attempt to decrypt garbage ciphertext -> should be rejected.
    bogus = base64.b64encode(b"this-is-not-valid-kms-ciphertext").decode()
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", bogus,
        "--grant-tokens", "xxxxxxxxxxx",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr