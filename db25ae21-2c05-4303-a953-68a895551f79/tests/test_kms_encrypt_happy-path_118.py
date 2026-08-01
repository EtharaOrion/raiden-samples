def test_encrypt_roundtrip_success(cli, kms, tmp_path):
    import base64, json

    # Seed prerequisite state: a usable ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
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
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Assert the effect via an independent read: decrypt round-trips
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext
    assert decrypt["KeyId"].endswith(key_id)