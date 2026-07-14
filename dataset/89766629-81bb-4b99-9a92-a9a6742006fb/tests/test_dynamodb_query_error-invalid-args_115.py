from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_invalid_args(cli, ddb_client):
    table_name = "QueryErrTbl"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table_name in ddb_client.list_tables()["TableNames"]

    # Query against a table with an oversized/nonexistent table name and no
    # valid key condition - expect a service-modeled validation error.
    bad_name = "x" * 600
    result = cli(
        "dynamodb", "query",
        "--table-name", bad_name,
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"abc"}}',
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr or "ResourceNotFoundException" in result.stderr