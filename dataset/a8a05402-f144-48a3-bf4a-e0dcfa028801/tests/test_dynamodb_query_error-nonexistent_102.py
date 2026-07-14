from _ddb_http import to_item, from_item, to_av, from_av


def test_query_nonexistent_table(cli, ddb_client):
    table_name = "NoSuchQueryTable"
    assert table_name not in ddb_client.list_tables()["TableNames"]
    result = cli(
        "dynamodb", "query",
        "--table-name", table_name,
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr