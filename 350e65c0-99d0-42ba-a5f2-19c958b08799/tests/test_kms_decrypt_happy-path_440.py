def test_decrypt_roundtrip_happy_path(cli, kms):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-message-123"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    blob = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent verification via kms rpc
    dec = kms.rpc("Decrypt", {"CiphertextBlob": blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id