from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_on_oversized_table_name(cli, ddb_client):
    long_name = "x" * 600
    result = cli("dynamodb", "query", "--table-name", long_name)
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "ResourceNotFoundException" in result.stderr