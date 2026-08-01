from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition(cli, ddb_client):
    table = "QueryMissingKeyCond"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "a"}})

    result = cli("dynamodb", "query", "--table-name", table)

    assert result.returncode != 0
    assert "ValidationException" in result.stderr

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "a"}})
    assert resp.get("Item") is not None