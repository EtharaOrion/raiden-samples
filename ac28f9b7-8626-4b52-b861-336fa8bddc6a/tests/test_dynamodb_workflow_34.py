from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_limits_twice_between(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf35Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf35Table",
                 "--item", '{"pk":{"S":"dl1"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf35Table", Key={"pk": {"S": "dl1"}})
    assert from_item(resp["Item"])["v"] == 1
