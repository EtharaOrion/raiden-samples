from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_table_nonexistent_raises(cli, ddb_client):
    table_name = "NoSuchTableForDelete"
    # Ensure the table does not exist.
    assert table_name not in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", table_name)
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    # Still absent.
    assert table_name not in ddb_client.list_tables()["TableNames"]