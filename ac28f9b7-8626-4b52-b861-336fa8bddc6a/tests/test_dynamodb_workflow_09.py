from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_adds_new_attribute(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf10Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf10Table",
                 "--item", '{"pk":{"S":"u1"},"a":{"S":"aa"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf10Table",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET b = :b",
                 "--expression-attribute-values", '{":b":{"S":"bb"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf10Table", Key={"pk": {"S": "u1"}})
    item = from_item(resp["Item"])
    assert item["a"] == "aa" and item["b"] == "bb"
