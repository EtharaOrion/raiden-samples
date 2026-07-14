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
        Item={"pk": {"S": "abc"}, "n": {"N": "5"}},
    )
    result = cli("dynamodb", "query", "--table-name", "QueryTbl")
    assert result.returncode != 0
    assert "ValidationException" in result.stderr