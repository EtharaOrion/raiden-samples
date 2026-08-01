def test_decrypt_round_trip_returns_original_plaintext(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "decrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-message"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli("kms", "decrypt", "--ciphertext-blob", ciphertext_blob)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id
    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext

    # independent read: decrypt the same blob via the raw API and confirm consistency
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext