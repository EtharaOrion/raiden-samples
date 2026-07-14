from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_getitem_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "WfTblNoSuchGet",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
