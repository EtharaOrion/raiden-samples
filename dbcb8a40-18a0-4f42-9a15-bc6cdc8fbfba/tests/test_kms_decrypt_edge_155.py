def test_decrypt_roundtrip_with_key_id(cli, kms):
    import base64, json

    create = kms.rpc("CreateKey", {"Description": "decrypt-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-message"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": plaintext_b64})
    ciphertext_blob = enc["CiphertextBlob"]

    result = cli(
        "kms", "decrypt",
        "--ciphertext-blob", ciphertext_blob,
        "--key-id", key_id,
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    decrypted = base64.b64decode(out["Plaintext"])
    assert decrypted == plaintext

    # Independent read-back: decrypt again through the backend directly.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id