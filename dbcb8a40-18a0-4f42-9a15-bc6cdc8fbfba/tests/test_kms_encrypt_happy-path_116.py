def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    # Seed prerequisite state: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

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
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Independent read-back: decrypt the ciphertext and verify round trip
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id