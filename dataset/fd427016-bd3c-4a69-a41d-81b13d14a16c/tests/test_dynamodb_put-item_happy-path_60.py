from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_creates_item(cli, ddb_client):
    table_name = "PutItemTable"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli(
        "dynamodb", "put-item",
        "--table-name", table_name,
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"},"s":{"S":"hello"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(
        TableName=table_name,
        Key={"pk": {"S": "abc"}},
    )
    item = resp.get("Item")
    assert item is not None
    assert item["pk"] == {"S": "abc"}
    assert item["n"] == {"N": "5"}
    assert item["s"] == {"S": "hello"}