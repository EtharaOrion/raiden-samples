def test_schedule_key_deletion_nonexistent_key_errors(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"
    result = cli("kms", "schedule-key-deletion", "--key-id", missing_key_id)
    assert result.returncode != 0
    assert "NotFound" in result.stderr

    listed = kms.rpc("ListKeys", {})
    ids = [k["KeyId"] for k in listed.get("Keys", [])]
    assert missing_key_id not in ids