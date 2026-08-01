def test_schedule_key_deletion_invalid_args(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "for invalid args test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert "attribute-definitions" in result.stderr.lower() or "unknown" in result.stderr.lower() or "argument" in result.stderr.lower()

    # State unchanged: key not scheduled for deletion
    describe = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert describe["KeyMetadata"]["KeyState"] != "PendingDeletion"