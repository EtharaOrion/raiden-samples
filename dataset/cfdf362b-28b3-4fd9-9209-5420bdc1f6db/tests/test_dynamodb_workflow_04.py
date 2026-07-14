from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_missing_fails(cli, ddb_client, tmp_path):
    assert "WfTblNoSuch1" not in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "delete-table", "--table-name", "WfTblNoSuch1")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
