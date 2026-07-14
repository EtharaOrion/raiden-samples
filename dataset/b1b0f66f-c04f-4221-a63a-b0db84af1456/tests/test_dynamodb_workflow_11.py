from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_idempotent_then_get(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFIdem",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "WFIdem",
        "--key", '{"pk":{"S":"ghost"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WFIdem", Key={"pk": {"S": "ghost"}}, ConsistentRead=True)
    assert "Item" not in resp
