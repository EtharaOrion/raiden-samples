from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_conditional_check_failed(cli, ddb_client):
    ddb_client.create_table(
        TableName="CondTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="CondTbl",
        Item={"pk": {"S": "item1"}, "v": {"S": "original"}},
    )
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "CondTbl",
        "--item", '{"pk":{"S":"item1"},"v":{"S":"updated"}}',
        "--condition-expression", "attribute_not_exists(pk)",
    )
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="CondTbl", Key={"pk": {"S": "item1"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["v"]["S"] == "original"