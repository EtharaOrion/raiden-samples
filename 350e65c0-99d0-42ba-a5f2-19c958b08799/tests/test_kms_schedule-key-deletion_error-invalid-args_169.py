def test_schedule_key_deletion_already_pending_invalid_state(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "sched-del-invalid-state"})
    key_id = key["KeyMetadata"]["KeyId"]

    # First schedule deletion succeeds
    first = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                "--pending-window-in-days", "7")
    assert first.returncode == 0

    desc = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc["KeyMetadata"]["KeyState"] == "PendingDeletion"

    # Second schedule deletion on an already-pending key must fail
    second = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                 "--pending-window-in-days", "7")
    assert second.returncode != 0
    assert "KMSInvalidStateException" in second.stderr

    # State unchanged
    desc2 = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert desc2["KeyMetadata"]["KeyState"] == "PendingDeletion"