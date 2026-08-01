def test_get_key_rotation_status_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {
        "Description": "rotation status invalid-argument test",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("EnableKeyRotation", {"KeyId": key_id})
    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is True

    result = cli(
        "kms",
        "get-key-rotation-status",
        "--key-id",
        "",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is True
    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "Enabled"