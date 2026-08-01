def test_schedule_key_deletion_happy_path(cli, kms, tmp_path):
    created = kms.rpc("CreateKey", {"Description": "to-delete"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms", "schedule-key-deletion",
        "--key-id", key_id,
        "--pending-window-in-days", "7",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    assert described["KeyMetadata"]["KeyState"] == "PendingDeletion"