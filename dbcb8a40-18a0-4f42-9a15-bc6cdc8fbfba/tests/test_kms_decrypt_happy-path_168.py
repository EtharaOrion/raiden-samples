def test_decrypt_round_trip_success(cli, kms, tmp_path):
    import json, base64

    # Seed: create a key and encrypt a known plaintext
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # Write ciphertext to a file so we can feed it as a blob
    cipher_file = tmp_path / "cipher.bin"
    cipher_file.write_bytes(base64.b64decode(ciphertext_b64))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{cipher_file}",
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Verify decrypted plaintext matches original
    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext

    # Independent read-back: decrypt directly via the raw client too
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext