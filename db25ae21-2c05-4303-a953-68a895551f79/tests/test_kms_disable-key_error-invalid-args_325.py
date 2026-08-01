def test_disable_key_invalid_key_id(cli, kms):
    bogus_key_id = "x" * 300
    result = cli("kms", "disable-key", "--key-id", bogus_key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "NotFound" in result.stderr