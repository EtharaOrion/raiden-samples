from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_set_overwrites_existing_attribute(cli, ddb_client):
    table = "UpdateOverwriteTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k1"}, "v": {"S": "original"}},
    )

    result = cli(
        "dynamodb", "update-item",
        "--table-name", table,
        "--key", '{"id":{"S":"k1"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"updated"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName=table, Key={"id": {"S": "k1"}})
    item = resp.get("Item")
    assert item is not None
    assert item["v"] == {"S": "updated"}