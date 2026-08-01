def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Seed a valid key so the service is reachable
    key = kms.rpc("CreateKey", {"Description": "decrypt-invalid-test"})
    key_id = key["KeyMetadata"]["KeyId"]
    assert key["KeyMetadata"]["KeyState"] == "Enabled"

    # Provide a bogus ciphertext blob that is not valid KMS ciphertext
    bogus = base64.b64encode(b"this-is-not-valid-kms-ciphertext").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr or \
           "InvalidKeyUsageException" in result.stderr

    # Assert key state is unchanged by the failed decrypt
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "Enabled"
    assert described["KeyMetadata"]["Enabled"] is True