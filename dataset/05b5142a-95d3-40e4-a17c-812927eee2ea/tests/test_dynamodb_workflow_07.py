from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "delete-table", "--table-name", "WfNoSuchTbl")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "WfNoSuchTbl" not in ddb_client.list_tables()["TableNames"]
