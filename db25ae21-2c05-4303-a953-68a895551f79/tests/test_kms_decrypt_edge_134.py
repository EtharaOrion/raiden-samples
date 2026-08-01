def test_decrypt_symmetric_default_roundtrip(cli, kms, tmp_path):
    import json, base64

    # Seed: create a symmetric encryption key
    create = kms.rpc("CreateKey", {"Description": "decrypt-edge-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to obtain a valid ciphertext blob
    plaintext = b"hello-kms-decrypt-edge"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # The CLI expects the ciphertext-blob as raw bytes; provide via fileb:// path
    blob_path = tmp_path / "ciphertext.bin"
    blob_path.write_bytes(base64.b64decode(ciphertext_b64))

    # Run command under test
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_path}",
        "--encryption-algorithm", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # The decrypted plaintext must round-trip to the original input
    assert base64.b64decode(out["Plaintext"]) == plaintext
    # The key used must resolve to our seeded key
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent read: confirm the key still describes fine
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True