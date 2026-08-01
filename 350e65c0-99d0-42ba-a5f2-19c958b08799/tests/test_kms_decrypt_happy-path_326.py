def test_decrypt_happy_path_roundtrip(cli, kms, tmp_path):
    import base64, json

    # Prerequisite: create a symmetric key
    create = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Encrypt a known plaintext to obtain ciphertext
    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    # Decrypt via CLI. --ciphertext-blob expects a fileb:// or blob; the CLI
    # decodes base64 for the blob argument automatically when given base64 text.
    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    # Assert round-trip: decrypted plaintext equals the original input
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent verification via kms client
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext