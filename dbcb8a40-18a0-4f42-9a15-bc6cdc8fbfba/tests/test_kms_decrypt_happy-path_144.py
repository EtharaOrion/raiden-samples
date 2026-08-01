def test_decrypt_roundtrip_happy_path(cli, kms):
    import base64, json

    # Seed: create a key and encrypt a known plaintext
    key = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-message"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test: decrypt the ciphertext
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    returned_plaintext = base64.b64decode(out["Plaintext"])
    assert returned_plaintext == plaintext
    assert out["KeyId"].endswith(key_id) or key_id in out["KeyId"]

    # Independent state verification: server-side decrypt round-trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext