def test_decrypt_roundtrip_returns_original_plaintext(cli, kms, tmp_path):
    import json, base64

    # Seed: create a symmetric key
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to get a valid ciphertext blob
    plaintext = b"top-secret-message"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # The CLI blob param expects raw bytes; write the ciphertext to a file and use fileb://
    blob_file = tmp_path / "ciphertext.bin"
    blob_file.write_bytes(base64.b64decode(ciphertext_b64))

    # Run the command under test
    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_file}",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # The returned Plaintext (base64) must decode to the original plaintext
    returned = base64.b64decode(out["Plaintext"])
    assert returned == plaintext

    # Independent verification via the raw kms client round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext