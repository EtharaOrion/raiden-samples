def test_enable_key_rotation_with_maximum_custom_period(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "key for custom rotation period test",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is False

    result = cli(
        "kms",
        "enable-key-rotation",
        "--key-id",
        key_id,
        "--rotation-period-in-days",
        "2560",
    )
    assert result.returncode == 0

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is True