def test_disable_key_rotation_rejects_unknown_flag_without_changing_state(cli, kms):
    created = kms.rpc("CreateKey", {
        "Description": "invalid disable-key-rotation arguments test",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "SYMMETRIC_DEFAULT",
    })
    key_id = created["KeyMetadata"]["KeyId"]
    kms.rpc("EnableKeyRotation", {"KeyId": key_id})

    result = cli(
        "kms",
        "disable-key-rotation",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    status = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert status["KeyRotationEnabled"] is True