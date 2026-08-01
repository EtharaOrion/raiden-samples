def test_decrypt_happy_path(cli, kms, tmp_path):
    import json, base64

    # Seed a symmetric KMS key
    create = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt some plaintext via the backend to obtain a valid ciphertext blob
    plaintext = b"hello-decrypt-happy-path"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    blob_b64 = enc["CiphertextBlob"]

    # Run the command under test: decrypt using the ciphertext blob
    result = cli("kms", "decrypt", "--ciphertext-blob", blob_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)

    # Assert the round trip: decrypted plaintext equals the original
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independently verify via the backend that this blob decrypts to the same plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext