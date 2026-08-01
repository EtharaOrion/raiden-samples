def test_schedule_key_deletion_error_nonexistent(cli, kms):
    fake_key_id = "12345678-1234-1234-1234-123456789012"
    result = cli("kms", "schedule-key-deletion", "--key-id", fake_key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    try:
        kms.rpc("DescribeKey", {"KeyId": fake_key_id})
        described = True
    except Exception:
        described = False
    assert not described