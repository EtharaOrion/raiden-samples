def test_decrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "decrypt-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-message-42"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].split("/")[-1].endswith(key_id) or key_id in out["KeyId"]

    # Independent read-back via kms.rpc to confirm decrypt behaviour
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext