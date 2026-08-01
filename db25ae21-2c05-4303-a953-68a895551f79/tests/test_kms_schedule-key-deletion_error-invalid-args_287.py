def test_schedule_key_deletion_already_pending_invalid_state(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "pending-deletion test"})
    key_id = created["KeyMetadata"]["KeyId"]

    # First schedule deletion — should succeed and set PendingDeletion
    first = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                "--pending-window-in-days", "7")
    assert first.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    # Second schedule deletion on a key already PendingDeletion — invalid state
    second = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                 "--pending-window-in-days", "7")
    assert second.returncode != 0
    assert not second.stdout.strip(), second.stdout
    assert "KMSInvalidStateException" in second.stderr

    # Key still exists and remains PendingDeletion
    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyState"] == "PendingDeletion"