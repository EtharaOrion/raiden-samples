from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_item_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "RealTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "GhostTbl",
                 "--item", '{"pk":{"S":"y"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr

    assert "GhostTbl" not in ddb_client.list_tables()["TableNames"]
