from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_then_get_absent(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfDelItem",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfDelItem", Item={"pk": {"S": "x"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelItem",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDelItem", Key={"pk": {"S": "x"}}, ConsistentRead=True)
    assert "Item" not in resp
