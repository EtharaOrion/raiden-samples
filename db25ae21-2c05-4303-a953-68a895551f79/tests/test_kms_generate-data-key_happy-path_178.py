def test_generate_data_key_happy_path(cli, kms, tmp_path):
    import json
    import base64

    key = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Plaintext should be a 256-bit (32 byte) key
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The returned ciphertext must decrypt back to the same plaintext via KMS
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or decrypted["KeyId"] == key_id