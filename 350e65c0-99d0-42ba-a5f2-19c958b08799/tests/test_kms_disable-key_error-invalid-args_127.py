def test_disable_key_missing_required_key_id(cli, kms):
    # Run disable-key without the required --key-id parameter
    result = cli("kms", "disable-key")
    assert result.returncode != 0
    # argparse-style missing-required-argument error
    assert "key-id" in result.stderr.lower() or "required" in result.stderr.lower()