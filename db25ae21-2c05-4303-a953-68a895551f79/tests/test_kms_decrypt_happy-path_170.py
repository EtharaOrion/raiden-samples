def test_decrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import base64, json

    # Seed: create a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext via the backend to obtain a ciphertext blob
    plaintext = b"hello-decrypt-roundtrip"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # The CLI expects the ciphertext blob as raw bytes (fileb://) or base64.
    # Write raw ciphertext bytes to a file and pass via fileb://.
    blob_path = tmp_path / "ciphertext.bin"
    blob_path.write_bytes(base64.b64decode(ciphertext_b64))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_path}",
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # The returned Plaintext (base64) must round-trip to the original plaintext
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent state assertion: the key used still describes correctly
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True

    # Independent decrypt via backend confirms same round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext