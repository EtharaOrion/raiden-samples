from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_large_number(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf49Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf49Table",
                 "--item", '{"pk":{"S":"ln1"},"big":{"N":"1000000000000"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf49Table", Key={"pk": {"S": "ln1"}})
    assert from_item(resp["Item"])["big"] == 1000000000000
