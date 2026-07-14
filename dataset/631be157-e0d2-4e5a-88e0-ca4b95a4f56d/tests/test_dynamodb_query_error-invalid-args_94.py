from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_expression(cli, ddb_client):
    ddb_client.create_table(
        TableName="QueryTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="QueryTbl",
        Item={"pk": {"S": "a"}, "v": {"N": "1"}},
    )

    result = cli("dynamodb", "query", "--table-name", "QueryTbl")

    assert result.returncode != 0
    assert "ValidationException" in result.stderr

    resp = ddb_client.get_item(TableName="QueryTbl", Key={"pk": {"S": "a"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["v"]["N"] == "1"