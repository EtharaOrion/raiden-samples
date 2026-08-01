def test_create_key_happy_path(cli, kms, tmp_path):
    import json, base64

    result = cli(
        "kms", "create-key",
        "--description", "my black-box test key",
        "--key-spec", "SYMMETRIC_DEFAULT",
        "--key-usage", "ENCRYPT_DECRYPT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    meta = out["KeyMetadata"]
    key_id = meta["KeyId"]
    assert key_id

    # Independent read-back via raw kms
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    dmeta = described["KeyMetadata"]
    assert dmeta["KeyId"] == key_id
    assert dmeta["Description"] == "my black-box test key"
    assert dmeta["KeyUsage"] == "ENCRYPT_DECRYPT"
    assert dmeta["Enabled"] is True
    assert dmeta["KeyState"] == "Enabled"

    # Confirm it is usable: Encrypt -> Decrypt round trip
    plaintext = b"round-trip-secret"
    pt_b64 = base64.b64encode(plaintext).decode()
    enc = kms.rpc("Encrypt", {"KeyId": key_id, "Plaintext": pt_b64})
    dec = kms.rpc("Decrypt", {"CiphertextBlob": enc["CiphertextBlob"]})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # It should be listed
    keys = kms.rpc("ListKeys", {})
    assert any(k["KeyId"] == key_id for k in keys["Keys"])