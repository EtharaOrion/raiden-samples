from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_missing_table_fails(cli, ddb_client, tmp_path):
    assert "WfGetNoTbl" not in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "get-item", "--table-name", "WfGetNoTbl",
                 "--key", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
