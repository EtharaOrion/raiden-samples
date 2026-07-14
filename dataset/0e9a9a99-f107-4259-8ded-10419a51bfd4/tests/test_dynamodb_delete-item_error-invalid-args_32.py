from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_conditional_check_failure(cli, ddb_client):
    table = "DelItemTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "item1"}, "status": {"S": "active"}},
    )
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"item1"}}',
        "--condition-expression", "#s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"inactive"}}',
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    assert resp.get("Item") is not None