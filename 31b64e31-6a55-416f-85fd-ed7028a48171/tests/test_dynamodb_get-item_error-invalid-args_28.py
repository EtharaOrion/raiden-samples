from _ddb_http import to_item, from_item, to_av, from_av


def test_get_item_missing_table_errors(cli, ddb_client):
    # Ensure the table does not exist.
    assert "NoSuchTbl" not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "get-item",
        "--table-name", "NoSuchTbl",
        "--key", '{"pk":{"S":"abc"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr