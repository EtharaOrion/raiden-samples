from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_item_missing_table(cli, ddb_client, tmp_path):
    before = ddb_client.list_tables()["TableNames"]
    assert "WfMissingPutTbl" not in before

    result = cli("dynamodb", "put-item", "--table-name", "WfMissingPutTbl",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
