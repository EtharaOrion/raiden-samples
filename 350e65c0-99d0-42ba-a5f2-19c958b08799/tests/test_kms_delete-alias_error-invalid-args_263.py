def test_delete_alias_empty_name_invalid(cli, kms):
    result = cli("kms", "delete-alias", "--alias-name", "")
    assert result.returncode != 0
    stderr = result.stderr.lower()
    assert (
        "notfound" in stderr
        or "validation" in stderr
        or "invalid" in stderr
        or "exception" in stderr
    )