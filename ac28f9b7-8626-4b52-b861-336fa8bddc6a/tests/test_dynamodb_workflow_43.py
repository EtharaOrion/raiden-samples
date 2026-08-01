from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_condition_not_exists_fails(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf44Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf44Table",
                 "--item", '{"pk":{"S":"cne1"},"v":{"S":"a"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf44Table",
                 "--key", '{"pk":{"S":"cne1"}}',
                 "--update-expression", "SET v = :v",
                 "--condition-expression", "attribute_not_exists(pk)",
                 "--expression-attribute-values", '{":v":{"S":"b"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf44Table", Key={"pk": {"S": "cne1"}})
    assert from_item(resp["Item"])["v"] == "a"
