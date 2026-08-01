def test_generate_data_key_happy_path(cli, kms, tmp_path):
    import json
    import base64

    create = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = create["KeyMetadata"]["KeyId"]

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

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32  # AES_256 = 32 bytes

    # Verify the returned ciphertext decrypts back to the plaintext via KMS
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert dec["Plaintext"] == out["Plaintext"]

    # And the decrypt used the same key
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id