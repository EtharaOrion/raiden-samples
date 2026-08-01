from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_missing_table_between_valid(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf58Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf58Table",
                 "--item", '{"pk":{"S":"v1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf58Ghost",
                 "--item", '{"pk":{"S":"v2"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf58Table", Key={"pk": {"S": "v1"}})
    assert "Item" in resp
