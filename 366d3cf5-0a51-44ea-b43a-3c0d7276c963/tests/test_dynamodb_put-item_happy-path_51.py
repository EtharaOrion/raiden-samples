from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_creates_observable_item(cli, ddb_client):
    table = "PutItemTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli(
        "dynamodb", "put-item",
        "--table-name", table,
        "--item", '{"pk":{"S":"item1"},"n":{"N":"42"},"s":{"S":"hello"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    item = resp.get("Item")
    assert item is not None
    assert item["pk"] == {"S": "item1"}
    assert item["n"] == {"N": "42"}
    assert item["s"] == {"S": "hello"}