def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    # Seed a valid key so the service is otherwise healthy.
    created = kms.rpc("CreateKey", {"Description": "decrypt-invalid-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    # Confirm the key exists and is usable.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["Enabled"] is True

    # Attempt to decrypt a bogus ciphertext blob that was never produced by Encrypt.
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", "bm90LWEtcmVhbC1jaXBoZXJ0ZXh0",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr

    # The seeded key remains intact and usable after the failed decrypt.
    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyId"] == key_id
    assert still["KeyMetadata"]["Enabled"] is True