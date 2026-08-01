def test_schedule_key_deletion_invalid_pending_window(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "test-invalid-window"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--pending-window-in-days", "366",
    )

    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "Validation" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] != "PendingDeletion"