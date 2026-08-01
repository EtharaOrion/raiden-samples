def test_list_aliases_limit_out_of_range(cli, kms):
    result = cli("kms", "list-aliases", "--limit", "1001")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Value" in result.stderr or "limit" in result.stderr.lower()

    # Ensure the invalid request did not disturb list-aliases functionality
    resp = kms.rpc("ListAliases", {})
    assert "Aliases" in resp