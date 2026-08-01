def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "encrypt-happy", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Assert the round trip via an independent Decrypt on the backend.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id