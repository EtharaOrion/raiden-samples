from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_creates_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="Products",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "Products",
        "--item", '{"pk":{"S":"widget"},"price":{"N":"42"},"name":{"S":"Widget"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Products", Key={"pk": {"S": "widget"}})
    item = resp.get("Item")
    assert item is not None
    assert item["pk"] == {"S": "widget"}
    assert item["price"] == {"N": "42"}
    assert item["name"] == {"S": "Widget"}