from _ddb_http import to_item, from_item, to_av, from_av


def test_put_item_creates_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="Tbl1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli(
        "dynamodb", "put-item",
        "--table-name", "Tbl1",
        "--item", '{"pk":{"S":"abc"},"n":{"N":"5"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl1", Key={"pk": {"S": "abc"}})
    item = resp.get("Item")
    assert item is not None
    assert item["pk"]["S"] == "abc"
    assert item["n"]["N"] == "5"