from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_absent_key(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfAbs1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfAbs1",
                 "--item", '{"pk":{"S":"present"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "WfAbs1",
                 "--key", '{"pk":{"S":"missing"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfAbs1", Key={"pk": {"S": "missing"}})
    assert "Item" not in resp
