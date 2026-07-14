from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_invalid_args(cli, ddb_client):
    ddb_client.create_table(
        TableName="QueryTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    long_name = "x" * 2048
    result = cli("dynamodb", "query", "--table-name", long_name)
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )