def test_enable_key_rotation_happy_path(cli, kms):
    key = kms.rpc(
        "CreateKey",
        {
            "Description": "key rotation test",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = key["KeyMetadata"]["KeyId"]

    initial = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert initial["KeyRotationEnabled"] is False

    result = cli("kms", "enable-key-rotation", "--key-id", key_id)

    assert result.returncode == 0
    status = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert status["KeyRotationEnabled"] is True