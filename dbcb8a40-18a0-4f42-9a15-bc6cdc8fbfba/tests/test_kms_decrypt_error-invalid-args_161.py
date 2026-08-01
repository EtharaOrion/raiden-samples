def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Seed a valid key so the service is functional
    created = kms.rpc("CreateKey", {"Description": "decrypt-error-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Verify the key exists and is enabled
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True

    # Build a bogus ciphertext blob that is NOT valid KMS ciphertext
    bogus = base64.b64encode(b"this-is-not-valid-kms-ciphertext").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr or \
           "InvalidKeyUsageException" in result.stderr

    # Ensure the seeded key is untouched by the failed decrypt
    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyId"] == key_id
    assert still["KeyMetadata"]["Enabled"] is True