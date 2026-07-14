from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_sets_attribute(cli, ddb_client):
    table = "UpdateTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "item1"}, "status": {"S": "old"}},
    )

    result = cli(
        "dynamodb", "update-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"item1"}}',
        "--update-expression", "SET #s = :v",
        "--expression-attribute-names", '{"#s":"status"}',
        "--expression-attribute-values", '{":v":{"S":"active"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["status"] == {"S": "active"}