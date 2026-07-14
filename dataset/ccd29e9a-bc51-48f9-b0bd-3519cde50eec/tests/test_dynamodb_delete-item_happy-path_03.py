from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_removes_existing_item(cli, ddb_client):
    table = "DelTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "item1"}, "n": {"N": "5"}},
    )
    assert ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}}).get("Item")

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"item1"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    assert resp.get("Item") is None