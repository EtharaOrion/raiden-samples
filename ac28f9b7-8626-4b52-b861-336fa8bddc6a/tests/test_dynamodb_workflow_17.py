from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_success(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf18Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf18Table",
                 "--item", '{"pk":{"S":"uc1"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf18Table",
                 "--key", '{"pk":{"S":"uc1"}}',
                 "--update-expression", "SET v = :new",
                 "--condition-expression", "v = :cur",
                 "--expression-attribute-values", '{":new":{"N":"2"},":cur":{"N":"1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf18Table", Key={"pk": {"S": "uc1"}})
    assert from_item(resp["Item"])["v"] == 2
