def test_schedule_key_deletion_pending_deletion_invalid_state(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "for invalid-state deletion test"})
    key_id = created["KeyMetadata"]["KeyId"]

    first = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                "--pending-window-in-days", "7")
    assert first.returncode == 0

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"

    second = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                 "--pending-window-in-days", "7")
    assert second.returncode != 0
    assert not second.stdout.strip(), second.stdout
    assert "KMSInvalidStateException" in second.stderr

    still = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert still["KeyMetadata"]["KeyState"] == "PendingDeletion"