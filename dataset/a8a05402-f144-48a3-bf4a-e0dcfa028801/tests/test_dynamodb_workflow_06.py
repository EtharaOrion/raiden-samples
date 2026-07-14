from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_item_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "put-item", "--table-name", "NoSuchTablePut",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
