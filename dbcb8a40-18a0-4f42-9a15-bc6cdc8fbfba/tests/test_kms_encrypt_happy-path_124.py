def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-data"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Independent read: decrypt via the raw kms client and verify round trip.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id