def test_generate_data_key_aes_128_roundtrip(cli, kms, tmp_path):
    import json
    import base64

    # Seed prerequisite state: create a symmetric encryption KMS key.
    create = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run command under test.
    result = cli(
        "kms", "generate-data-key",
        "--key-id", key_id,
        "--key-spec", "AES_128",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # AES_128 => 16 bytes of plaintext key material.
    plaintext_bytes = base64.b64decode(out["Plaintext"])
    assert len(plaintext_bytes) == 16

    # Independent read: decrypt the returned CiphertextBlob and verify it
    # matches the returned plaintext data key (round trip through the backend).
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert base64.b64decode(decrypt["Plaintext"]) == plaintext_bytes
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id