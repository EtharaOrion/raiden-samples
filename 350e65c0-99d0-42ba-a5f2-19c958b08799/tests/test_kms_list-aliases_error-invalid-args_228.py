def test_list_aliases_limit_out_of_range(cli, kms):
    before = kms.rpc("ListAliases", {})
    result = cli("kms", "list-aliases", "--limit", "1001")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "Value" in result.stderr
    after = kms.rpc("ListAliases", {})
    assert "Aliases" in after