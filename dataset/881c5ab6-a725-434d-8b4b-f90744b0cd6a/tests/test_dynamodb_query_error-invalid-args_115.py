from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_expression_fails(cli, ddb_client):
    table_name = "QueryTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table_name,
        Item={"pk": {"S": "abc"}, "n": {"N": "5"}},
    )

    result = cli("dynamodb", "query", "--table-name", table_name)

    assert result.returncode != 0
    assert "ValidationException" in result.stderr

    resp = ddb_client.get_item(TableName=table_name, Key={"pk": {"S": "abc"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["n"]["N"] == "5"