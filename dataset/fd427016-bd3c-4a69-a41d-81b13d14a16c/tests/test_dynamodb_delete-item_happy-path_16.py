from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_removes_item(cli, ddb_client):
    table = "DeleteItemTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "abc"}, "n": {"N": "5"}},
    )
    pre = ddb_client.get_item(TableName=table, Key={"pk": {"S": "abc"}})
    assert pre.get("Item") is not None

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"abc"}}',
    )
    assert result.returncode == 0

    post = ddb_client.get_item(TableName=table, Key={"pk": {"S": "abc"}})
    assert post.get("Item") is None