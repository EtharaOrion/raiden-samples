from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_conditional_fail_preserves(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf30Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf30Table",
                 "--item", '{"pk":{"S":"p"},"v":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf30Table",
                 "--key", '{"pk":{"S":"p"}}',
                 "--update-expression", "SET v = :b",
                 "--expression-attribute-values", '{":b":{"S":"b"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf30Table",
                 "--key", '{"pk":{"S":"p"}}',
                 "--update-expression", "SET v = :c",
                 "--condition-expression", "v = :expect",
                 "--expression-attribute-values", '{":c":{"S":"c"},":expect":{"S":"a"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf30Table", Key={"pk": {"S": "p"}})
    assert from_item(resp["Item"])["v"] == "b"
