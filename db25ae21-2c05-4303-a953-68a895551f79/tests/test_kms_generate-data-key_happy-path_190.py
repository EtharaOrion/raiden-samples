def test_generate_data_key_happy_path(cli, kms):
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
    assert out["KeyId"]

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # Verify the ciphertext decrypts back to the same plaintext via the key
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext

    # The KeyId in the response should reference our seeded key
    desc = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert desc["KeyMetadata"]["KeyId"] == key_id