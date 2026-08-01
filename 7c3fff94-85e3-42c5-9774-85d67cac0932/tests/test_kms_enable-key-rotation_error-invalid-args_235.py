def test_enable_key_rotation_missing_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "key for missing enable-key-rotation argument test",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "KeySpec": "SYMMETRIC_DEFAULT",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is False

    result = cli("kms", "enable-key-rotation")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is False