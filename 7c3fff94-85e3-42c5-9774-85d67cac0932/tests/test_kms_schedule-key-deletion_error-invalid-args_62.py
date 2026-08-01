def test_schedule_key_deletion_rejects_invalid_arguments(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key must remain active after invalid deletion request"},
    )
    key_id = created["KeyMetadata"]["KeyId"]
    assert created["KeyMetadata"]["KeyState"] == "Enabled"

    result = cli(
        "kms",
        "schedule-key-deletion",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "Enabled"
    assert metadata["Enabled"] is True