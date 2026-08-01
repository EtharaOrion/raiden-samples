def test_decrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import base64, json

    # Seed a KMS key
    key = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to obtain a ciphertext blob
    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Decrypt expects a fileb:// blob (raw bytes); write decoded blob to file
    blob_path = tmp_path / "cipher.blob"
    blob_path.write_bytes(base64.b64decode(ciphertext_blob))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_path}",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # KeyId should match the key used
    assert key_id in out["KeyId"]

    # Verify the round trip: decoded Plaintext equals input
    returned_pt = base64.b64decode(out["Plaintext"])
    assert returned_pt == plaintext

    # Independent read-back through the raw kms client on the same ciphertext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert key_id in dec["KeyId"]