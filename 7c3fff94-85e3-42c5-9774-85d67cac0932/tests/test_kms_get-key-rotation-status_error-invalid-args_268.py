def test_get_key_rotation_status_rejects_unknown_attribute_definitions(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "rotation-status invalid-arguments test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("EnableKeyRotation", {"KeyId": key_id})
    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is True

    result = cli(
        "kms",
        "get-key-rotation-status",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is True