def test_decrypt_round_trip_happy_path(cli, kms):
    import base64, json

    # Seed: create a symmetric key
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    # Prepare plaintext and encrypt via backend
    plaintext = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # The decrypted plaintext must round-trip to the original
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent read: decrypting the same blob via backend yields original plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext