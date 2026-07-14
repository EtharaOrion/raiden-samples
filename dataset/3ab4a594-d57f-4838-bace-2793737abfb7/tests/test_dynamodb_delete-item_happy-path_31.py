from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_removes_existing_item(cli, ddb_client):
    table = "DeleteItemHappy"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "item1"}, "data": {"S": "hello"}},
    )
    pre = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    assert pre.get("Item") is not None

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"item1"}}',
    )
    assert result.returncode == 0

    post = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    assert post.get("Item") is None