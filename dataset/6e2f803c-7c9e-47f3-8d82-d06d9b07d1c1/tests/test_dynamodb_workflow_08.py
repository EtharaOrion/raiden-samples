from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_then_get_absent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblDelItem1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblDelItem1", Item={"pk": {"S": "d1"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblDelItem1",
                 "--key", '{"pk":{"S":"d1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblDelItem1", Key={"pk": {"S": "d1"}})
    assert "Item" not in resp
