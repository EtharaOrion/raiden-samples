def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    # Seed a valid key so the service is otherwise functional
    created = kms.rpc("CreateKey", {"Description": "decrypt-invalid-blob"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Provide garbage that is not a valid ciphertext blob produced by KMS
    bogus = "bm90LWEtcmVhbC1jaXBoZXJ0ZXh0LWJsb2I="

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    # Category substring for a modeled service error on this backend
    stderr = result.stderr or ""
    assert (
        "InvalidCiphertextException" in stderr
        or "KMSInternalException" in stderr
        or "Exception" in stderr
    )

    # Key state unaffected — service still functional
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["KeyState"] == "Enabled"