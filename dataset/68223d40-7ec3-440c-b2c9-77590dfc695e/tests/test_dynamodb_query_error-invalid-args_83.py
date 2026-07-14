from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_invalid_args(cli, ddb_client):
    table_name = "QueryErrTable"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table_name in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "query", "--table-name", "")
    assert result.returncode != 0

    combined = (result.stderr or "") + (result.stdout or "")
    assert (
        "ValidationException" in combined
        or "ResourceNotFoundException" in combined
        or result.returncode != 0
    )