def test_disable_key_rotation_missing_key_id(cli, kms):
    key = kms.rpc("CreateKey", {
        "Description": "rotation remains enabled after invalid CLI invocation"
    })
    key_id = key["KeyMetadata"]["KeyId"]

    kms.rpc("EnableKeyRotation", {"KeyId": key_id})

    result = cli("kms", "disable-key-rotation")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    status = kms.rpc("GetKeyRotationStatus", {"KeyId": key_id})
    assert status["KeyRotationEnabled"] is True