def test_encrypt_invalid_key_id_not_found(cli, kms):
    bogus_key_id = "x" * 300
    result = cli("kms", "encrypt", "--key-id", bogus_key_id, "--plaintext", "aGVsbG8=")
    assert result.returncode != 0
    assert "NotFound" in result.stderr or "NotFoundException" in result.stderr