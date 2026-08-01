def test_decrypt_roundtrip_with_key_id(cli, kms, tmp_path):
    import base64, json

    # Seed: create a symmetric key
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext
    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    # The CLI blob argument accepts base64 text via fileb:// or a raw file;
    # here provide the ciphertext bytes through a file with fileb://
    blob_path = tmp_path / "ciphertext.bin"
    blob_path.write_bytes(base64.b64decode(ciphertext_b64))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", "fileb://" + str(blob_path),
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Verify the decrypted plaintext matches the original
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent read-back: decrypt via raw RPC yields the original plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64, "KeyId": key_id})
    assert base64.b64decode(dec["Plaintext"]) == plaintext