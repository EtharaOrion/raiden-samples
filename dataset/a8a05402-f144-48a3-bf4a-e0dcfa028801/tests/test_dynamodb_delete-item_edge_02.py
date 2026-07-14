from _ddb_http import to_item, from_item, to_av, from_av


def test_delete_item_idempotent_on_missing_key(cli, ddb_client):
    table = "IdempDeleteTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=table, Item={"id": {"S": "exists"}})

    result = cli(
        "dynamodb", "delete-item",
        "--table-name", table,
        "--key", '{"id":{"S":"never-existed"}}',
    )
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName=table, Key={"id": {"S": "never-existed"}})
    assert resp.get("Item") is None

    other = ddb_client.get_item(TableName=table, Key={"id": {"S": "exists"}})
    assert other.get("Item") is not None
    assert other["Item"]["id"]["S"] == "exists"