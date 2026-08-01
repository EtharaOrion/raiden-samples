def test_decrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json
    import base64

    # Seed a KMS key
    create = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt plaintext to obtain a valid ciphertext blob
    plaintext = b"hello decrypt roundtrip"
    plaintext_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # aws cli --ciphertext-blob accepts a fileb:// or blob value; write raw bytes to file
    blob_file = tmp_path / "ciphertext.blob"
    blob_file.write_bytes(base64.b64decode(ciphertext_blob))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", "fileb://" + str(blob_file),
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # KeyId should be reported
    assert key_id in out["KeyId"]

    # The decrypted plaintext must match the original input
    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext

    # Independent verification via kms round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext