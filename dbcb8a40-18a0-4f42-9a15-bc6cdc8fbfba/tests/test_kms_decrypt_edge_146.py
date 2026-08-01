def test_decrypt_roundtrip_success(cli, kms, tmp_path):
    import json, base64

    # Seed: create a key and encrypt a known plaintext
    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"hello decrypt world"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Run the command under test: decrypt the ciphertext
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Verify round-trip: decrypted plaintext matches original
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent read-back: decrypt via raw rpc must also round-trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext