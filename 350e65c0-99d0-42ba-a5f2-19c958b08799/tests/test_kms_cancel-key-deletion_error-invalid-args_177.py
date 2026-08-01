def test_cancel_key_deletion_invalid_args(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "test invalid args"})
    key_id = create["KeyMetadata"]["KeyId"]
    kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})

    result = cli(
        "kms", "cancel-key-deletion",
        "--key-id", key_id,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # The command should not have taken effect; key remains PendingDeletion
    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"