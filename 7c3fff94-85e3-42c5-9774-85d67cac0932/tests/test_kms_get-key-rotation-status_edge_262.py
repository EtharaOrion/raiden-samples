def test_get_key_rotation_status_enabled(cli, kms, tmp_path):
    import json

    created = kms.rpc(
        "CreateKey",
        {
            "Description": "rotation status test key",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    kms.rpc("EnableKeyRotation", {"KeyId": key_id})

    result = cli(
        "kms",
        "get-key-rotation-status",
        "--key-id",
        key_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["KeyRotationEnabled"] is True

    status = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert status["KeyRotationEnabled"] is True