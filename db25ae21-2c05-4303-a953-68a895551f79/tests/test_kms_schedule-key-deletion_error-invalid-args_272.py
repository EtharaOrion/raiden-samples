def test_schedule_key_deletion_empty_key_id(cli, kms):
    result = cli("kms", "schedule-key-deletion", "--key-id", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "Invalid" in result.stderr