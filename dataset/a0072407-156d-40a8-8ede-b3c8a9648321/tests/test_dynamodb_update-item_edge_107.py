from _ddb_http import to_item, from_item, to_av, from_av


def test_update_item_add_increments_counter(cli, ddb_client):
    table = "CounterTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k1"}, "c": {"N": "0"}},
    )
    result = cli(
        "dynamodb", "update-item",
        "--table-name", table,
        "--key", '{"id":{"S":"k1"}}',
        "--update-expression", "ADD c :inc",
        "--expression-attribute-values", '{":inc":{"N":"1"}}',
    )
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName=table, Key={"id": {"S": "k1"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["c"] == {"N": "1"}