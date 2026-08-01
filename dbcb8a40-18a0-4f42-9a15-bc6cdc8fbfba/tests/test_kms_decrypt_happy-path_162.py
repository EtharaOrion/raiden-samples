def test_decrypt_round_trip_returns_plaintext(cli, kms, tmp_path):
    import json, base64

    # Seed a KMS key
    create = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to produce ciphertext for the CLI to decrypt
    secret = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(secret).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Structural assertions on the decrypt response
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id
    returned = base64.b64decode(out["Plaintext"])
    assert returned == secret

    # Independent read-back: KMS itself must decrypt the same ciphertext to the same plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == secret