from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_then_get_item_absent(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFDel1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WFDel1", Item={"pk": {"S": "gone"}, "v": {"N": "1"}})
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WFDel1",
        "--key", '{"pk":{"S":"gone"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WFDel1", Key={"pk": {"S": "gone"}}, ConsistentRead=True)
    assert "Item" not in resp
