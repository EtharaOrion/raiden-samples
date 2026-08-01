def test_generate_data_key_aes256_roundtrip(cli, kms):
    import json, base64

    create = kms.rpc("CreateKey", {"Description": "gen-data-key-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert out["KeyId"]

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # The encrypted data key should decrypt back to the plaintext data key
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext

    # And the decrypt should reference the same key we generated under
    described = kms.rpc("DescribeKey", {"KeyId": decrypt["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id