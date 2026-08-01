def test_schedule_key_deletion_invalid_flag(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "invalid-flag-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert "not-a-real-flag" in result.stderr or "Unknown option" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] != "PendingDeletion"