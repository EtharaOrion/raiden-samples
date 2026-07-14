from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_fails(cli, ddb_client):
    table = "QueryErrTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "query", "--table-name", table)
    assert result.returncode != 0
    assert "ValidationException" in result.stderr