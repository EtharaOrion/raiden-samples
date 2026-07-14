from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_expression_invalid_args(cli, ddb_client):
    ddb_client.create_table(
        TableName="QTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "query", "--table-name", "QTbl")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr