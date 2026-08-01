def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Seed: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-data-v20"
    b64_plaintext = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", b64_plaintext,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext = out["CiphertextBlob"]
    assert ciphertext

    # Independent read: decrypt via kms and verify round trip
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id