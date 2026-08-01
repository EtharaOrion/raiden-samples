def test_encrypt_symmetric_default_roundtrip(cli, kms):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "encrypt-edge-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-database-password-42"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--encryption-algorithm", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext = out["CiphertextBlob"]
    assert ciphertext

    # Independent read: decrypt the ciphertext via the backend and assert round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id