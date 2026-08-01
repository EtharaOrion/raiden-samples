def test_disable_key_rotation_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {
        "Description": "rotation state sentinel",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "SYMMETRIC_DEFAULT",
    })
    key_id = created["KeyMetadata"]["KeyId"]
    kms.rpc("EnableKeyRotation", {"KeyId": key_id})

    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is True

    result = cli("kms", "disable-key-rotation", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is True