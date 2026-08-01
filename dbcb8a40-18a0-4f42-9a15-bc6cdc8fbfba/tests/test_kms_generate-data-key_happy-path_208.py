def test_generate_data_key_happy_path(cli, kms, tmp_path):
    import json
    import base64

    create = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--number-of-bytes", "32",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Plaintext" in out
    assert "CiphertextBlob" in out
    assert "KeyId" in out

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The returned KeyId must map to our key
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # Verify the encrypted data key decrypts back to the plaintext
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext