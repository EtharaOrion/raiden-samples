def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "encrypt-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-database-password"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    decrypted = base64.b64decode(dec["Plaintext"])
    assert decrypted == plaintext

    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id