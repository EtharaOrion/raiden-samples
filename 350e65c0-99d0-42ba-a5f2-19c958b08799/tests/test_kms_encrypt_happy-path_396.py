def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Prerequisite: create a symmetric ENCRYPT_DECRYPT key
    created = kms.rpc("CreateKey", {"Description": "encrypt-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-data"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Independent read: decrypt the ciphertext via kms and assert round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    decrypted = base64.b64decode(dec["Plaintext"])
    assert decrypted == plaintext

    # The decrypt should resolve to the same key we used
    assert dec["KeyId"].endswith(key_id) or key_id in dec["KeyId"]