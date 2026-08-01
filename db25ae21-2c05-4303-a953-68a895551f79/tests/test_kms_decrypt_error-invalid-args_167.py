def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64

    # Seed a valid key so the service is otherwise operational.
    created = kms.rpc("CreateKey", {"Description": "decrypt-error-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["KeyState"] == "Enabled"

    # Craft a garbage ciphertext blob that is not valid KMS ciphertext.
    bad_blob = base64.b64encode(b"this-is-not-valid-kms-ciphertext").decode("ascii")

    result = cli("kms", "decrypt", "--ciphertext-blob", bad_blob)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    # The seeded key must still be present and usable (Encrypt->Decrypt round trip).
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyId"] == key_id
    assert described["KeyMetadata"]["Enabled"] is True

    plaintext = base64.b64encode(b"round-trip-check").decode("ascii")
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert dec["Plaintext"] == plaintext