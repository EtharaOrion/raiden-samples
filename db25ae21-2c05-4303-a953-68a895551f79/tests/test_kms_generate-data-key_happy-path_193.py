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
    assert out["KeyId"].endswith(key_id) or key_id in out["KeyId"]

    plaintext = out["Plaintext"]
    # AES_256 -> 32 bytes plaintext
    assert len(base64.b64decode(plaintext)) == 32

    # The returned CiphertextBlob must decrypt back to the same plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert dec["Plaintext"] == plaintext
    assert dec["KeyId"].endswith(key_id) or key_id in dec["KeyId"]