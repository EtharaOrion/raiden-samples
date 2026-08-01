def test_decrypt_round_trip_recovers_plaintext(cli, kms):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    pt_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_b64,
        "--key-id", key_id,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # Independent read-back via raw RPC confirms decryptability
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or key_id in dec["KeyId"]