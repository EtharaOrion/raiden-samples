def test_encrypt_round_trip_happy_path(cli, kms, tmp_path):
    import json, base64

    # Prerequisite: create a key to encrypt with
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-password"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Assert the effect via an independent read: Decrypt round-trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    decrypted = base64.b64decode(dec["Plaintext"])
    assert decrypted == plaintext