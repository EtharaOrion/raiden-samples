from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_removes_existing_item(cli, ddb_client):
    ddb_client.create_table(
        TableName="DelTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="DelTbl",
        Item={"pk": {"S": "item1"}, "data": {"S": "hello"}},
    )
    before = ddb_client.get_item(TableName="DelTbl", Key={"pk": {"S": "item1"}})
    assert before.get("Item") is not None

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "DelTbl",
        "--key", '{"pk":{"S":"item1"}}',
    )
    assert result.returncode == 0

    after = ddb_client.get_item(TableName="DelTbl", Key={"pk": {"S": "item1"}})
    assert after.get("Item") is None