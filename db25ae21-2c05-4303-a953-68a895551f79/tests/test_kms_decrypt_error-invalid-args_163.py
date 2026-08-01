def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Seed a valid key so the service is otherwise functional
    created = kms.rpc("CreateKey", {})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Provide a bogus ciphertext blob that is not a valid KMS ciphertext
    bogus = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr

    # Key still exists and is usable
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True