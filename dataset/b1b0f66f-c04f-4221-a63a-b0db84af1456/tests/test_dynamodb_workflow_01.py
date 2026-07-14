from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_item_then_get_item_reflects_change(cli, ddb_client):
    ddb_client.create_table(
        TableName="WFUpd1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="WFUpd1", Item={"pk": {"S": "a1"}, "status": {"S": "old"}})
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "WFUpd1",
        "--key", '{"pk":{"S":"a1"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"new"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WFUpd1", Key={"pk": {"S": "a1"}}, ConsistentRead=True)
    from _ddb_http import from_item
    assert from_item(resp["Item"])["status"] == "new"
