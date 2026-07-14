from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_table_invalid_long_name(cli, ddb_client):
    long_name = "x" * 512
    result = cli("dynamodb", "delete-table", "--table-name", long_name)
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "ResourceNotFoundException" in result.stderr