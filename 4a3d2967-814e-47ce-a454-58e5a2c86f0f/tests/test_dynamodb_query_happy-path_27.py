from _ddb_http import to_item, from_item, to_av, from_av


def test_query_by_partition_key(cli, ddb_client):
    import json

    table = "QueryTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p1"}, "sk": {"S": "a"}, "v": {"N": "10"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p1"}, "sk": {"S": "b"}, "v": {"N": "20"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p2"}, "sk": {"S": "c"}, "v": {"N": "30"}},
    )

    result = cli(
        "dynamodb", "query",
        "--table-name", table,
        "--key-condition-expression", "pk = :pkval",
        "--expression-attribute-values", '{":pkval":{"S":"p1"}}',
    )

    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out["Count"] == 2
    returned_sks = sorted(item["sk"]["S"] for item in out["Items"])
    assert returned_sks == ["a", "b"]

    verify = ddb_client.query(
        TableName=table,
        KeyConditionExpression="pk = :pkval",
        ExpressionAttributeValues={":pkval": {"S": "p1"}},
    )
    assert verify["Count"] == 2
    verify_sks = sorted(item["sk"]["S"] for item in verify["Items"])
    assert verify_sks == ["a", "b"]