from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_if_not_exists(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf41Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf41Table",
                 "--item", '{"pk":{"S":"ine1"},"v":{"N":"7"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf41Table",
                 "--key", '{"pk":{"S":"ine1"}}',
                 "--update-expression", "SET v = if_not_exists(v, :d)",
                 "--expression-attribute-values", '{":d":{"N":"99"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf41Table", Key={"pk": {"S": "ine1"}})
    assert from_item(resp["Item"])["v"] == 7
