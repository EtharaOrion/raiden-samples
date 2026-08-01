def test_create_key_happy_path(cli, kms, tmp_path):
    desc = "integration-test-key-happy-path"
    result = cli(
        "kms", "create-key",
        "--description", desc,
        "--key-spec", "SYMMETRIC_DEFAULT",
        "--key-usage", "ENCRYPT_DECRYPT",
        "--tags", "TagKey=env,TagValue=test",
    )
    assert result.returncode == 0, result.stderr

    import json
    out = json.loads(result.stdout)
    key_id = out["KeyMetadata"]["KeyId"]
    assert key_id

    # Independent read-back via kms RPC
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    meta = described["KeyMetadata"]
    assert meta["KeyId"] == key_id
    assert meta["Description"] == desc
    assert meta["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert meta["Enabled"] is True
    assert meta["KeyState"] == "Enabled"

    # Verify the key is functional via an encrypt->decrypt round trip
    import base64
    plaintext = b"round-trip-secret"
    enc = kms.rpc("Encrypt", {
        "KeyId": key_id,
        "Plaintext": base64.b64encode(plaintext).decode(),
    })
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # Verify the tag was applied
    tags = kms.rpc("ListResourceTags", {"KeyId": key_id})["Tags"]
    assert any(t["TagKey"] == "env" and t["TagValue"] == "test" for t in tags)