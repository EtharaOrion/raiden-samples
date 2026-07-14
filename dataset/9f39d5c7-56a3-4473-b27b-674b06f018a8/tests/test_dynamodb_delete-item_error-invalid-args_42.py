from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_missing_table_errors(cli, ddb_client):
    # The table does not exist; deleting from it must fail with ResourceNotFoundException.
    table_name = "NoSuchTable_DeleteItem"
    assert table_name not in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table_name,
        "--key", '{"pk":{"S":"abc"}}',
    )

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    # State assertion: table still absent.
    assert table_name not in ddb_client.list_tables()["TableNames"]