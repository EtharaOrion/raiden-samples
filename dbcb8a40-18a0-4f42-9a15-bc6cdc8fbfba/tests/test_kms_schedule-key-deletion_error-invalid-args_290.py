def test_schedule_key_deletion_invalid_pending_window(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "test key for invalid window"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "schedule-key-deletion", "--key-id", key_id,
                 "--pending-window-in-days", "366")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "ValidationError" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] != "PendingDeletion"