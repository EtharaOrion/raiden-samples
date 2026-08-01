def test_list_aliases_invalid_limit(cli, kms):
    # Limit above the allowed maximum (1-1000) must be rejected client-side.
    result = cli("kms", "list-aliases", "--limit", "1001")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Value" in result.stderr or "Limit" in result.stderr or "limit" in result.stderr

    # The service state must still be intact and queryable.
    resp = kms.rpc("ListAliases", {})
    assert "Aliases" in resp