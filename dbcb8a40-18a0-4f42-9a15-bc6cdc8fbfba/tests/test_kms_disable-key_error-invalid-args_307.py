def test_disable_key_invalid_arn_error(cli, kms):
    result = cli("kms", "disable-key", "--key-id", "not-a-valid-arn:::")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr or "InvalidArnException" in result.stderr