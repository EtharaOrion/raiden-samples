def test_enable_key_rotation_nonexistent(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "rotation error control key"})
    control_key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("GetKeyRotationStatus", {"KeyId": control_key_id})
    assert before["KeyRotationEnabled"] is False

    missing_alias = f"alias/missing-{control_key_id}"
    result = cli(
        "kms",
        "enable-key-rotation",
        "--key-id",
        missing_alias,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": control_key_id})
    assert after["KeyRotationEnabled"] is False