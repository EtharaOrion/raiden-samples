from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_then_getitem_absent(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfDel1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfDel1", Item={"pk": {"S": "d1"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfDel1",
                 "--key", '{"pk":{"S":"d1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDel1", Key={"pk": {"S": "d1"}})
    assert "Item" not in resp
