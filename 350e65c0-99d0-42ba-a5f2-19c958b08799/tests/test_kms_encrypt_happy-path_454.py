def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    # Seed: create a symmetric ENCRYPT_DECRYPT key
    created = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = created["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-payload-19"
    b64_plaintext = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", b64_plaintext,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Independent read: decrypt the ciphertext via kms and assert the round trip
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or decrypted["KeyId"] == key_id