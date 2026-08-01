def test_cancel_key_deletion_missing_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "key pending deletion"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "ScheduleKeyDeletion",
        {"KeyId": key_id, "PendingWindowInDays": 7},
    )

    result = cli("kms", "cancel-key-deletion")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "PendingDeletion"
    assert metadata["Enabled"] is False