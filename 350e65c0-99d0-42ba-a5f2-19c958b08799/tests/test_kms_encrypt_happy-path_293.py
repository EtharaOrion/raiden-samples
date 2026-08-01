def test_encrypt_roundtrip_happy_path(cli, kms):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "encrypt-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-data-1234"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--encryption-algorithm", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Independent read: decrypt the ciphertext and verify round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id