def test_decrypt_with_grant_tokens_roundtrip(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "decrypt-grant-tokens-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-payload-round-trip"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
        "--grant-tokens", "xxxxxxxxxx",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert base64.b64decode(out["Plaintext"]) == plaintext
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent verification via raw kms client
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext