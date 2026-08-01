from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_then_put_condition(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf48Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf48Table",
                 "--item", '{"pk":{"S":"up1"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "Wf48Table",
                 "--key", '{"pk":{"S":"up1"}}',
                 "--update-expression", "SET v = :v",
                 "--expression-attribute-values", '{":v":{"N":"2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf48Table",
                 "--item", '{"pk":{"S":"up1"},"v":{"N":"3"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf48Table", Key={"pk": {"S": "up1"}})
    assert from_item(resp["Item"])["v"] == 2
