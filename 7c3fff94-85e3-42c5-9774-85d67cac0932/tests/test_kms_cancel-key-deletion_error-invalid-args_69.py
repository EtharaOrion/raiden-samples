def test_cancel_key_deletion_rejects_unknown_flag(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid-args cancel deletion test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("ScheduleKeyDeletion", {"KeyId": key_id, "PendingWindowInDays": 7})
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "PendingDeletion"

    result = cli(
        "kms",
        "cancel-key-deletion",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyState"] == "PendingDeletion"