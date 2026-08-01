from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_multiple_sets(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf24Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf24Table",
                 "--item", '{"pk":{"S":"ms1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf24Table",
                 "--key", '{"pk":{"S":"ms1"}}',
                 "--update-expression", "SET a = :a, b = :b",
                 "--expression-attribute-values", '{":a":{"S":"x"},":b":{"N":"9"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf24Table", Key={"pk": {"S": "ms1"}})
    item = from_item(resp["Item"])
    assert item["a"] == "x" and item["b"] == 9
