def test_schedule_key_deletion_invalid_args(cli, kms):
    create = kms.rpc("CreateKey", {})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "attribute-definitions" in result.stderr

    describe = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert describe["KeyMetadata"]["KeyState"] != "PendingDeletion"