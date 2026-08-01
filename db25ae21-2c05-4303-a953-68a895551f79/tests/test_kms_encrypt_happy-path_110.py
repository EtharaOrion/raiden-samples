def test_encrypt_roundtrip_success(cli, kms, tmp_path):
    import base64, json

    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"top-secret-payload"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Independent read: decrypt the ciphertext via the backend and verify round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert key_id in dec["KeyId"]