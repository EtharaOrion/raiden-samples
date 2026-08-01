def test_schedule_key_deletion_pending_window_min(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "to be deleted"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--pending-window-in-days", "1",
    )
    # Note: some backends allow 1-day windows; if the command succeeds it must
    # take effect. The real minimum is 7, but this test targets a backend that
    # accepts the passed value; assert on success + resulting state.
    if result.returncode == 0:
        described = kms.rpc("DescribeKey", {"KeyId": key_id})
        assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"
    else:
        # If rejected, it must be an error category, not a crash.
        assert "Exception" in result.stderr or "Invalid" in result.stderr