def test_encrypt_roundtrip_via_decrypt(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "encrypt-edge"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"secret-database-password-12345"
    b64_plain = base64.b64encode(plaintext).decode()

    result = cli("kms", "encrypt", "--key-id", key_id,
                 "--plaintext", b64_plain)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id