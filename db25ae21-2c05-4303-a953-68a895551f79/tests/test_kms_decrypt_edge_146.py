def test_decrypt_roundtrip_recovers_plaintext(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "decrypt-roundtrip"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-message-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_b64 = enc["CiphertextBlob"]

    blob_path = tmp_path / "ciphertext.bin"
    blob_path.write_bytes(base64.b64decode(ciphertext_b64))

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", f"fileb://{blob_path}",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or key_id in out["KeyId"]
    assert base64.b64decode(out["Plaintext"]) == plaintext

    # independent read via kms rpc to confirm the ciphertext decrypts to the same plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext