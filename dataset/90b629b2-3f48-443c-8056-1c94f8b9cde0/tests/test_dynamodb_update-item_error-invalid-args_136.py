from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_missing_update_expression_flag(cli, ddb_client):
    ddb_client.create_table(
        TableName="Tbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="Tbl1",
        Item={"pk": {"S": "a"}, "status": {"S": "old"}},
    )
    result = cli(
        "dynamodb", "update-item",
        "--table-name", "Tbl1",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"new"}}',
        "--condition-expression", "attribute_exists(nonexistent_attr)",
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl1", Key={"pk": {"S": "a"}})
    assert resp.get("Item", {}).get("status", {}).get("S") == "old"