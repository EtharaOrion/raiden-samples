def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    # Seed valid state to ensure server is functional
    created = kms.rpc("CreateKey", {"Description": "decrypt-error-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["KeyState"] == "Enabled"

    # Attempt to decrypt garbage ciphertext that is not valid KMS ciphertext
    import base64
    bogus = base64.b64encode(b"this-is-not-valid-kms-ciphertext").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr

    # Key remains in a healthy, describable state
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True