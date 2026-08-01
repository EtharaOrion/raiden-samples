def test_enable_key_empty_key_id_rejected(cli, kms):
    result = cli("kms", "enable-key", "--key-id", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "ValidationException" in result.stderr or "Invalid" in result.stderr