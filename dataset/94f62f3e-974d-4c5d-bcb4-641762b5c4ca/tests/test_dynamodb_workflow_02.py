from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_then_getitem_absent(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf_DelGet1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="Wf_DelGet1", Item={"pk": {"S": "d1"}, "v": {"S": "x"}})
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "Wf_DelGet1",
        "--key", '{"pk":{"S":"d1"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf_DelGet1", Key={"pk": {"S": "d1"}})
    assert "Item" not in resp
