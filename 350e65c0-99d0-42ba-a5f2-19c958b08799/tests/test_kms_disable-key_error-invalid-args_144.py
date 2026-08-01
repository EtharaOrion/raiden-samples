def test_disable_key_invalid_arn(cli, kms):
    result = cli("kms", "disable-key", "--key-id", "not-a-valid-key-id")
    assert result.returncode != 0
    assert "NotFound" in result.stderr or "InvalidArn" in result.stderr