def test_get_key_rotation_status_rejects_unknown_flag(cli, kms):
    created = kms.rpc("CreateKey", {
        "Description": "invalid get-key-rotation-status arguments test"
    })
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKeyRotation", {"KeyId": key_id})
    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is False

    result = cli(
        "kms",
        "get-key-rotation-status",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is False
    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True