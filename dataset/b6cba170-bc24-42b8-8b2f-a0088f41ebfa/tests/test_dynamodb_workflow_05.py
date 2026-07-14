from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_item_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "WFNoSuchPutTable" not in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "put-item", "--table-name", "WFNoSuchPutTable",
                 "--item", '{"pk":{"S":"z"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
