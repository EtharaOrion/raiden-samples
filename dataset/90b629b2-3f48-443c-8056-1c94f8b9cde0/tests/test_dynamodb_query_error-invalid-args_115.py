from _ddb_http import to_item, from_item, to_av, from_av


def test_query_missing_key_condition_invalid_args(cli, ddb_client):
    table = "QueryInvalidArgsTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "a"}})

    # Query with an oversized/invalid table name and no key condition at all.
    bad_name = "x" * 600
    result = cli("dynamodb", "query", "--table-name", bad_name)
    assert result.returncode != 0
    assert (
        "ValidationException" in result.stderr
        or "ResourceNotFoundException" in result.stderr
    )

    # The real table remains intact and queryable.
    resp = ddb_client.query(
        TableName=table,
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "a"}},
    )
    assert resp["Count"] == 1