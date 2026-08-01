def test_schedule_key_deletion_requires_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "key must remain unchanged after invalid deletion request"},
    )
    metadata = created["KeyMetadata"]
    key_id = metadata["KeyId"]
    initial_state = metadata["KeyState"]
    initial_enabled = metadata["Enabled"]

    result = cli("kms", "schedule-key-deletion")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    current = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert current["KeyId"] == key_id
    assert current["KeyState"] == initial_state == "Enabled"
    assert current["Enabled"] is initial_enabled is True