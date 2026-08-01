def test_encrypt_roundtrip_happy_path(cli, kms):
    import json, base64

    # Seed: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"Description": "encrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-password-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Independent read: decrypt the ciphertext via kms and assert round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    decrypted = base64.b64decode(dec["Plaintext"])
    assert decrypted == plaintext

    # The decrypt should reference our key
    assert key_id in dec["KeyId"]