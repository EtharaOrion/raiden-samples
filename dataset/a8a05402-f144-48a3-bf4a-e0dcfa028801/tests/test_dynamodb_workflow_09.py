from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_no_mutation(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    table = "WfUpdCond"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", table,
                 "--item", '{"pk":{"S":"m1"},"cnt":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", table,
                 "--key", '{"pk":{"S":"m1"}}',
                 "--update-expression", "SET cnt = :new",
                 "--condition-expression", "cnt = :expect",
                 "--expression-attribute-values",
                 '{":new":{"N":"99"},":expect":{"N":"5"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "m1"}})
    assert from_item(resp["Item"])["cnt"] == 1
