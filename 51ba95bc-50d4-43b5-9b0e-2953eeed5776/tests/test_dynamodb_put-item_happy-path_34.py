from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_creates_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="Books",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "Books",
        "--item", '{"pk":{"S":"b1"},"title":{"S":"Dune"},"pages":{"N":"412"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Books", Key={"pk": {"S": "b1"}})
    item = resp.get("Item")
    assert item is not None
    assert item["title"] == {"S": "Dune"}
    assert item["pages"] == {"N": "412"}