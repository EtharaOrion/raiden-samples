from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_missing_expr_values_fails(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf50Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf50Table",
                 "--item", '{"pk":{"S":"me1"},"v":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf50Table",
                 "--key", '{"pk":{"S":"me1"}}',
                 "--update-expression", "SET v = :missing")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf50Table", Key={"pk": {"S": "me1"}})
    assert from_item(resp["Item"])["v"] == "a"
