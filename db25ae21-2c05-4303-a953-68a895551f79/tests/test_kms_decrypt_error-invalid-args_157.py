def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Seed a valid key so the service is healthy; the failure comes from bad ciphertext.
    created = kms.rpc("CreateKey", {"Description": "decrypt-error-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Confirm the key exists and is usable before the negative test.
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True

    # Feed garbage that is validly base64-encoded but is not real KMS ciphertext.
    bogus_blob = base64.b64encode(b"this-is-not-valid-kms-ciphertext").decode("ascii")

    result = cli("kms", "decrypt", "--ciphertext-blob", bogus_blob)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    # State assertion: the seeded key is untouched / still describable after the failure.
    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyId"] == key_id
    assert still["KeyMetadata"]["KeyState"] == "Enabled"