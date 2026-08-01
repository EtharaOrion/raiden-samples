from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_missing_table_then_create_then_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl22",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl22",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl22",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl22", Key={"pk": {"S": "a"}})
    assert "Item" in resp
