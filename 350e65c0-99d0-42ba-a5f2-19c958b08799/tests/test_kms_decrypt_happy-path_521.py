def test_decrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import json
    import base64

    # Seed: create a symmetric key
    create = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext via the backend
    plaintext = b"secret round trip payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test: decrypt the ciphertext blob
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Decrypted plaintext (base64) must match the original input
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent verification via backend Decrypt
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext