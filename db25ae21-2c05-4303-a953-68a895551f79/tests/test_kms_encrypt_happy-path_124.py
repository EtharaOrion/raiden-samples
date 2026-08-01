def test_encrypt_roundtrip_happy_path(cli, kms, tmp_path):
    import json, base64

    key = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-database-password"
    b64_plain = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", b64_plain,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or key_id in decrypted["KeyId"]