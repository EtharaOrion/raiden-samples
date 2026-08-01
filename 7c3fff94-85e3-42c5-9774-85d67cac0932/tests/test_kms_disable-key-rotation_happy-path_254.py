def test_disable_key_rotation_disables_automatic_rotation(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "key for disable-key-rotation test",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("EnableKeyRotation", {"KeyId": key_id})
    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is True

    result = cli("kms", "disable-key-rotation", "--key-id", key_id)
    assert result.returncode == 0

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is False