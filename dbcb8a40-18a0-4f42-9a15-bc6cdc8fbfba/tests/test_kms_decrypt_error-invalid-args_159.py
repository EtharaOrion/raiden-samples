def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    # Seed a valid key so the service is exercised, but pass a bogus ciphertext blob.
    key = kms.rpc("CreateKey", {"Description": "decrypt-error-test"})
    key_id = key["KeyMetadata"]["KeyId"]
    assert key_id

    # Verify the key exists and is enabled before the operation under test.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "Enabled"

    # Craft an invalid/garbage ciphertext blob (base64 of arbitrary bytes,
    # not produced by any KMS Encrypt op) — decryption must fail.
    import base64
    bogus_blob = base64.b64encode(b"this-is-not-valid-kms-ciphertext").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus_blob)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    # The service rejects an unparseable/incorrect ciphertext blob.
    assert (
        "InvalidCiphertextException" in result.stderr
        or "IncorrectKeyException" in result.stderr
    )

    # Key state is unaffected by the failed decrypt.
    after = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert after["KeyMetadata"]["KeyState"] == "Enabled"