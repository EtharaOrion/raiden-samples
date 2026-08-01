def test_decrypt_invalid_ciphertext_blob(cli, kms, tmp_path):
    import base64, json

    # Seed a valid key so the service is functional; the failure must be
    # due to the garbage ciphertext, not a missing key.
    created = kms.rpc("CreateKey", {"Description": "decrypt-invalid-cipher-test"})
    key_id = created["KeyMetadata"]["KeyId"]
    assert key_id

    # Confirm the key is usable (round-trip) so we know the error below is
    # specifically about the invalid ciphertext.
    plaintext = b"round-trip-check"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # Now attempt to decrypt garbage bytes that are NOT a valid KMS ciphertext.
    bad_blob = base64.b64encode(b"this-is-not-a-valid-kms-ciphertext-blob").decode()

    result = cli("kms", "decrypt", "--ciphertext-blob", bad_blob)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr

    # The seeded key remains valid and usable afterwards.
    md = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert md["KeyId"] == key_id
    assert md["Enabled"] is True