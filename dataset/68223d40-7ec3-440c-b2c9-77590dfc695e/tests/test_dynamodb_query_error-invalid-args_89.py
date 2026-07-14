from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_invalid(cli, ddb_client):
    table_name = "QueryErrTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table_name in ddb_client.list_tables()["TableNames"]

    result = cli(
        "dynamodb", "query",
        "--table-name", table_name,
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"abc"}, "malformed"',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "Invalid JSON" in result.stderr