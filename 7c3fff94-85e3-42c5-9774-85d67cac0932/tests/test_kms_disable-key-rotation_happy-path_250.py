def test_disable_key_rotation_happy_path(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key for disable-key-rotation test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("EnableKeyRotation", {"KeyId": key_id})
    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is True

    result = cli(
        "kms",
        "disable-key-rotation",
        "--key-id",
        key_id,
    )
    assert result.returncode == 0

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is False