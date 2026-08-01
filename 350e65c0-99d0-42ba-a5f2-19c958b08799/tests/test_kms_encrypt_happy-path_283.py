def test_encrypt_happy_path_roundtrip(cli, kms):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "encrypt happy path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-password-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Independently decrypt via kms and assert round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id