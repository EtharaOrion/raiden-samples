def test_encrypt_round_trip_happy_path(cli, kms, tmp_path):
    import base64, json

    key = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-database-password"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Independent read: decrypt via the raw kms client and verify round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id