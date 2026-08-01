from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_table_name_too_long(cli, ddb_client):
    long_name = "x" * 300
    result = cli("dynamodb", "delete-table", "--table-name", long_name)
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    assert long_name not in ddb_client.list_tables()["TableNames"]