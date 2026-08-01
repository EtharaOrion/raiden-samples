def test_encrypt_happy_path_roundtrip(cli, kms):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-database-password-42"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64
    assert isinstance(ciphertext_b64, str)

    # Independent read: decrypt via the raw API and assert the round trip.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id