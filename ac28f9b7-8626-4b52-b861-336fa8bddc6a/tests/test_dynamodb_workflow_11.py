from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_missing_key_creates_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf12Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf12Table",
                 "--key", '{"pk":{"S":"new1"}}',
                 "--update-expression", "SET c = :c",
                 "--expression-attribute-values", '{":c":{"N":"7"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf12Table", Key={"pk": {"S": "new1"}})
    assert from_item(resp["Item"])["c"] == 7
