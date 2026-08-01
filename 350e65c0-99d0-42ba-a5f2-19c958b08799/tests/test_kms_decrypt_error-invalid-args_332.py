def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Provide a bogus ciphertext blob that was never produced by KMS.
    bogus = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert "InvalidCiphertext" in result.stderr

    # Sanity: seed a real key and confirm a genuine round trip still works,
    # proving the failure above is specific to the invalid blob.
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    plaintext = base64.b64encode(b"hello world").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == plaintext