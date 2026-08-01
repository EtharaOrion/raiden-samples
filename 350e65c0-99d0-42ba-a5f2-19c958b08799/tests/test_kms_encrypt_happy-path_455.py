def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Seed prerequisite state: create a symmetric ENCRYPT_DECRYPT key.
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-database-password"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run command under test.
    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Independently verify effect: decrypt the produced ciphertext must yield original plaintext.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # The decrypt should reference the same key.
    assert key_id in dec["KeyId"]