def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Seed a valid key so the service is functional
    created = kms.rpc("CreateKey", {"Description": "decrypt-invalid-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Confirm the key exists and is enabled (baseline state before the failing call)
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True

    # Craft a bogus ciphertext blob that is NOT a valid KMS ciphertext
    bogus = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert "InvalidCiphertextException" in result.stderr

    # Verify the seeded key is still intact and usable afterward (state unchanged)
    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyId"] == key_id
    assert still["KeyMetadata"]["Enabled"] is True

    # Sanity: a real encrypt/decrypt round trip still works on this key
    pt = base64.b64encode(b"hello-world").decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == pt