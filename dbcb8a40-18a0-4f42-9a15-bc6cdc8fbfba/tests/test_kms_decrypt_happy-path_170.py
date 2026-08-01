def test_decrypt_round_trip_recovers_plaintext(cli, kms, tmp_path):
    import base64, json

    # Seed a KMS key
    create = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to produce ciphertext to decrypt
    plaintext = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # The CLI expects the ciphertext-blob as a blob; write raw bytes to a file
    # and reference it via fileb:// so aws cli reads it as binary.
    cipher_file = tmp_path / "cipher.bin"
    cipher_file.write_bytes(base64.b64decode(ciphertext_b64))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{cipher_file}",
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].split("/")[-1].endswith(key_id) or key_id in out["KeyId"]

    # The decrypted Plaintext (base64) must round-trip back to the input
    recovered = base64.b64decode(out["Plaintext"])
    assert recovered == plaintext

    # Independent verification: decrypt via the raw API also yields the plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # Key still exists and is enabled
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["Enabled"] is True