def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import base64, json

    key = kms.rpc("CreateKey", {"Description": "encrypt-happy"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-database-password-42"
    b64_plaintext = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", b64_plaintext,
        "--encryption-algorithm", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext = out["CiphertextBlob"]
    assert ciphertext

    # Independent read: decrypt via kms and assert round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id