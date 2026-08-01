from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_nonexistent_after_list(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf42Ghost" not in ddb_client.list_tables()["TableNames"]
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf42Ghost")
    assert rd.returncode != 0
    assert "ResourceNotFoundException" in rd.stderr
