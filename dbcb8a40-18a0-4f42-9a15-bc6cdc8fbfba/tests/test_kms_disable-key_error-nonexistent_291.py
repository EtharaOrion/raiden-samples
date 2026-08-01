def test_disable_key_error_nonexistent(cli, kms, tmp_path):
    missing_key_id = "00000000-1111-2222-3333-444444444444"
    result = cli("kms", "disable-key", "--key-id", missing_key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr