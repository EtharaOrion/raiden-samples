def test_generate_data_key_number_of_bytes(cli, kms, tmp_path):
    import json
    import base64

    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli("kms", "generate-data-key", "--key-id", key_id, "--number-of-bytes", "32")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    # verify the returned encrypted data key round-trips via Decrypt
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id