def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Seed prerequisite: create an ENCRYPT_DECRYPT symmetric key
    create = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-data-v14"
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
    assert ciphertext_blob

    # Assert the effect independently via a Decrypt round trip through kms
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    decrypted = base64.b64decode(decrypt["Plaintext"])
    assert decrypted == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id