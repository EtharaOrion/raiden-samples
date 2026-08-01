def test_cancel_key_deletion_happy_path_restores_key(cli, kms):
    import uuid

    created = kms.rpc(
        "CreateKey",
        {"Description": "cancel-key-deletion-happy-" + uuid.uuid4().hex},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc(
        "ScheduleKeyDeletion",
        {"KeyId": key_id, "PendingWindowInDays": 7},
    )
    pending = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert pending["KeyState"] == "PendingDeletion"

    result = cli("kms", "cancel-key-deletion", "--key-id", key_id)
    assert result.returncode == 0, result.stderr

    restored = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert restored["KeyId"] == key_id
    assert restored["KeyState"] != "PendingDeletion"
    assert "DeletionDate" not in restored
