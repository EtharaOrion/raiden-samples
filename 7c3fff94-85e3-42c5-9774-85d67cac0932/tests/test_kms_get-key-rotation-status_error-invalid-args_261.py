def test_get_key_rotation_status_missing_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "rotation status argument test"})
    key_id = created["KeyMetadata"]["KeyId"]
    before = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})

    result = cli("kms", "get-key-rotation-status")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    after = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert after["KeyRotationEnabled"] == before["KeyRotationEnabled"]
    assert kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]["KeyId"] == key_id