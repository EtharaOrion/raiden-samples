def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    # Prerequisite: create an ENCRYPT_DECRYPT symmetric key.
    create = kms.rpc("CreateKey", {"Description": "encrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test.
    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Independently verify: decrypt the returned ciphertext yields the original plaintext.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id