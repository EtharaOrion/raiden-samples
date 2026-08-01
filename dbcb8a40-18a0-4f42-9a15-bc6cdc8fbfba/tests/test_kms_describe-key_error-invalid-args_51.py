def test_describe_key_missing_required_key_id(cli, kms):
    result = cli("kms", "describe-key")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "key-id" in result.stderr.lower() or "usage" in result.stderr.lower()