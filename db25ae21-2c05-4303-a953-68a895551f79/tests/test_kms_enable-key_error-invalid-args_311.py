def test_enable_key_nonexistent_returns_not_found(cli, kms):
    result = cli(
        "kms", "enable-key",
        "--key-id", "00000000-0000-0000-0000-000000000000",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr