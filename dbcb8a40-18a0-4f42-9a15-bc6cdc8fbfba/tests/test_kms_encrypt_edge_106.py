def test_encrypt_roundtrip_success(cli, kms, tmp_path):
    import json, base64

    # Seed prerequisite state: create a key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-database-password"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run command under test
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext = out["CiphertextBlob"]
    assert isinstance(ciphertext, str) and ciphertext

    # Assert the effect via an independent Decrypt round trip
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    decrypted = base64.b64decode(decrypt["Plaintext"])
    assert decrypted == plaintext
    assert key_id in decrypt["KeyId"]