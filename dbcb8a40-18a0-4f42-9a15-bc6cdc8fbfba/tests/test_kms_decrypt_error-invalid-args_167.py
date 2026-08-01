def test_decrypt_invalid_ciphertext_blob(cli, kms):
    import base64

    # Seed a real key so the service is functional and only the ciphertext is bad.
    created = kms.rpc("CreateKey", {"Description": "decrypt-error-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Attempt to decrypt garbage that was never produced by Encrypt.
    bogus = base64.b64encode(b"this-is-not-valid-ciphertext-metadata").decode()
    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    # Service surfaces an error category (e.g. InvalidCiphertextException /
    # KMSInternalException) — match on the Exception category substring.
    assert "Exception" in result.stderr

    # Key state is unaffected by the failed decrypt.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True