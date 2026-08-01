def test_decrypt_invalid_ciphertext(cli, kms, tmp_path):
    import base64

    # Seed prerequisite state: a valid key exists so the service is functional.
    create = kms.rpc("CreateKey", {"Description": "decrypt-invalid-test"})
    key_id = create["KeyMetadata"]["KeyId"]
    assert key_id

    # Verify the key is usable via an Encrypt->Decrypt round trip through the backend.
    plaintext = b"round-trip-sanity"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # Now run the command under test with a bogus ciphertext blob.
    bogus = base64.b64encode(b"this-is-not-valid-ciphertext-metadata").decode()
    result = cli("kms", "decrypt", "--ciphertext-blob", bogus)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidCiphertextException" in result.stderr

    # The valid key must still be intact/usable after the failed decrypt.
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True