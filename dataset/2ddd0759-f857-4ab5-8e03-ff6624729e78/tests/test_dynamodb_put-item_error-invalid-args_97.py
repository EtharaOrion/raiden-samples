from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_conditional_check_failure(cli, ddb_client):
    table = "PutItemCondTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "abc"}, "v": {"S": "original"}},
    )

    result = cli(
        "dynamodb", "put-item",
        "--table-name", table,
        "--item", '{"pk":{"S":"abc"},"v":{"S":"replaced"}}',
        "--condition-expression", "attribute_not_exists(pk)",
    )

    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "abc"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["v"] == {"S": "original"}