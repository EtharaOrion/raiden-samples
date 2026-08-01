def test_generate_data_key_missing_key_id(cli, kms, tmp_path):
    result = cli("kms", "generate-data-key")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "key-id" in result.stderr.lower() or "keyid" in result.stderr.lower()