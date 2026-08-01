def test_describe_key_invalid_key_id(cli, kms):
    invalid_key_id = "x" * 2048
    result = cli("kms", "describe-key", "--key-id", invalid_key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr
    assert (
        "NotFoundException" in stderr
        or "InvalidArnException" in stderr
        or "ValidationException" in stderr
        or "Invalid" in stderr
    )