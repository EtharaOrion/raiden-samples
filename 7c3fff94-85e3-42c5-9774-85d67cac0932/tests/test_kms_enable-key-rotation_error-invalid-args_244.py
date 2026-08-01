def test_enable_key_rotation_rejects_unknown_attribute_definitions(cli, kms):
    created = kms.rpc("CreateKey", {})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert before["KeyRotationEnabled"] is False

    result = cli(
        "kms",
        "enable-key-rotation",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] is False