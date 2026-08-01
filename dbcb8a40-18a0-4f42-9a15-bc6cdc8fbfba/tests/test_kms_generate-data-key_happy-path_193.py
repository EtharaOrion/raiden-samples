def test_generate_data_key_happy_path(cli, kms, tmp_path):
    import json
    import base64

    create = kms.rpc("CreateKey", {"Description": "gen-data-key-test"})
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
    assert len(plaintext) == 32

    # Assert the encrypted data key can be decrypted back to the same plaintext
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # Assert the key used still exists and is enabled
    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyId"] == key_id
    assert desc["KeyMetadata"]["Enabled"] is True