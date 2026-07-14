from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_then_get(ddb_client, cli, tmp_path):
    ddb_client.create_table(
        TableName="WfDel1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WfDel1", Item={"pk": {"S": "gone"}, "v": {"N": "1"}})
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WfDel1",
        "--key", '{"pk":{"S":"gone"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfDel1", Key={"pk": {"S": "gone"}})
    assert "Item" not in resp
