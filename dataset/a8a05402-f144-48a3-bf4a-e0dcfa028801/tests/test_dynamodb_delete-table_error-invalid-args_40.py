from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_table_nonexistent_resource_error(cli, ddb_client):
    table_name = "TblDeleteMissing"
    # Ensure the table does not exist so delete-table must fail.
    assert table_name not in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "delete-table", "--table-name", table_name)

    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    # State assertion: table still absent after the failed delete.
    assert table_name not in ddb_client.list_tables()["TableNames"]