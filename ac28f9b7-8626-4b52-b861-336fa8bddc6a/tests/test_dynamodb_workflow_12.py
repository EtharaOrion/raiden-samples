from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_overwrite_then_read(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf13Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf13Table",
                 "--item", '{"pk":{"S":"o1"},"v":{"S":"one"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf13Table",
                 "--item", '{"pk":{"S":"o1"},"v":{"S":"two"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf13Table", Key={"pk": {"S": "o1"}})
    assert from_item(resp["Item"])["v"] == "two"
