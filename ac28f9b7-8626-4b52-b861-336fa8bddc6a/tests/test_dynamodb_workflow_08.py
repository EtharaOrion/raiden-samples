from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describelimits_then_put(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf9Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf9Table",
                 "--item", '{"pk":{"S":"d1"},"x":{"N":"42"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf9Table", Key={"pk": {"S": "d1"}})
    assert from_item(resp["Item"])["x"] == 42
