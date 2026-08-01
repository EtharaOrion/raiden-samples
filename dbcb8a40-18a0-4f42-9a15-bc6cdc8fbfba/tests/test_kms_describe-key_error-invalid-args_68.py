def test_describe_key_invalid_arn_error(cli, kms):
    result = cli("kms", "describe-key", "--key-id", "arn:aws:kms:us-east-1:invalid")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr or "InvalidArnException" in result.stderr