def test_decrypt_invalid_ciphertext_blob(cli, kms):
    import base64

    # Seed a valid key and produce a real ciphertext to have valid state around
    key = kms.rpc("CreateKey", {"Description": "decrypt-invalid-arg-test"})
    key_id = key["KeyMetadata"]["KeyId"]
    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["KeyState"] == "Enabled"

    # Corrupt/invalid ciphertext blob (not a genuine KMS ciphertext)
    bad_blob = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bad_blob)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr

    # Key state unaffected by the failed decrypt
    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["KeyState"] == "Enabled"