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
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert "KeyId" in out

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Verify the returned KeyId refers to our key via an independent read
    desc = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert desc["KeyMetadata"]["KeyId"] == key_id

    # Verify the CiphertextBlob decrypts back to the same plaintext data key
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert dec["Plaintext"] == out["Plaintext"]