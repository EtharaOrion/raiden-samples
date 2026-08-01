def test_schedule_key_deletion_invalid_key_id(cli, kms):
    bad_key_id = "x" * 300
    result = cli("kms", "schedule-key-deletion", "--key-id", bad_key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "Invalid" in result.stderr or "NotFound" in result.stderr