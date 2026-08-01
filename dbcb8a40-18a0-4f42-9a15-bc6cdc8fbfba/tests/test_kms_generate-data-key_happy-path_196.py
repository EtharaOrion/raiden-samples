def test_generate_data_key_happy_path(cli, kms, tmp_path):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_256",
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Plaintext must be 32 bytes (AES_256)
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Verify the CiphertextBlob decrypts back to the same plaintext via KMS
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # And the decrypt is bound to our key
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id