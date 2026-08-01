def test_encrypt_roundtrip_via_cli(cli, kms, tmp_path):
    import json, base64

    # Seed: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"secret-data-1234"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run encrypt via CLI
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--output", "json",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Independent read: decrypt the ciphertext and assert round trip
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext

    # The decrypt resolves to the same key we encrypted with
    assert decrypted["KeyId"].endswith(key_id) or key_id in decrypted["KeyId"]