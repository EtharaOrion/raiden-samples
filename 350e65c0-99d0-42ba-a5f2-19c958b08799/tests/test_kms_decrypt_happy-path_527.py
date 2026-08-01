def test_decrypt_round_trip_recovers_plaintext(cli, kms):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"the-secret-message"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent read-back via kms rpc to confirm decrypt works on same blob
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or key_id in dec["KeyId"]