from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_table_missing_fails(cli, ddb_client):
    result = cli("dynamodb", "delete-table", "--table-name", "NoSuchTableWF404")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "NoSuchTableWF404" not in ddb_client.list_tables()["TableNames"]
