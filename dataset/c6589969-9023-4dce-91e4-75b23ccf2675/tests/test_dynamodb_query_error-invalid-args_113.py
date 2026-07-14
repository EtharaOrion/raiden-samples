from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_expression(cli, ddb_client):
    ddb_client.create_table(
        TableName="QTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName="QTbl",
        Item={"pk": {"S": "a"}},
    )
    result = cli(
        "dynamodb", "query",
        "--table-name", "QTbl",
        "--filter-expression", "attribute_exists(pk)",
    )
    assert result.returncode != 0
    assert "ValidationException" in result.stderr