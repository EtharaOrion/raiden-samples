from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_add_and_verify_untouched(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf55Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf55Table",
                 "--item", '{"pk":{"S":"au1"},"a":{"S":"stay"},"b":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf55Table",
                 "--key", '{"pk":{"S":"au1"}}',
                 "--update-expression", "SET b = :b",
                 "--expression-attribute-values", '{":b":{"N":"5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf55Table", Key={"pk": {"S": "au1"}})
    item = from_item(resp["Item"])
    assert item["a"] == "stay" and item["b"] == 5
