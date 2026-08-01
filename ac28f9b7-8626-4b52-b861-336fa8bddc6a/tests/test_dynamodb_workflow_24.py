from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_missing_table_then_create_succeeds(cli, ddb_client):
    result = cli("dynamodb", "put-item", "--table-name", "Wf25Table",
                 "--item", '{"pk":{"S":"z1"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    ddb_client.create_table(
        TableName="Wf25Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf25Table",
                 "--item", '{"pk":{"S":"z1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf25Table", Key={"pk": {"S": "z1"}})
    assert "Item" in resp
