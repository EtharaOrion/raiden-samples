def test_decrypt_round_trip_happy_path(cli, kms):
    import base64, json

    # Seed a symmetric key
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to obtain a ciphertext blob
    plaintext = b"hello decrypt world"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    # The decrypted plaintext must equal what we encrypted
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out.get("KeyId", "").endswith(key_id) or key_id in out.get("KeyId", "")

    # Independent verification via the raw client
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext