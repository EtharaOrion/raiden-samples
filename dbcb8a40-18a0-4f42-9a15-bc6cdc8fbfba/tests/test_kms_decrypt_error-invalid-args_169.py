def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    # Seed a valid key and produce a real ciphertext so the backend is exercised
    key = kms.rpc("CreateKey", {"Description": "decrypt-invalid-args"})
    key_id = key["KeyMetadata"]["KeyId"]

    import base64
    plaintext = b"hello world"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    real_blob = enc["CiphertextBlob"]

    # Sanity: verify the real ciphertext round-trips through the CLI-adjacent state
    dec = kms.rpc("Decrypt", {"CiphertextBlob": real_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # Now attempt to decrypt garbage ciphertext that is not valid KMS ciphertext.
    bogus = base64.b64encode(b"not-a-real-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    # Key remains present and usable after the failed decrypt attempt
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True