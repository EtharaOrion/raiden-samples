from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfGMT1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "WfGMT1" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "get-item", "--table-name", "NoSuchTableWfGMT",
                 "--key", '{"pk":{"S":"a1"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
