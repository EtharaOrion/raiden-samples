from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_missing_table_update_then_create_put(cli, ddb_client):
    result = cli("dynamodb", "update-item", "--table-name", "Wf78Table",
                 "--key", '{"pk":{"S":"x"}}',
                 "--update-expression", "SET a = :a",
                 "--expression-attribute-values", '{":a":{"S":"y"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    ddb_client.create_table(
        TableName="Wf78Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf78Table",
                 "--item", '{"pk":{"S":"x"},"a":{"S":"y"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf78Table", Key={"pk": {"S": "x"}})
    assert from_item(resp["Item"])["a"] == "y"
