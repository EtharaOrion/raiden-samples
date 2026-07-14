from _ddb_http import to_item, from_item, to_av, from_av


def test_query_partition_key_returns_matching_items(cli, ddb_client):
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
        Item={"pk": {"S": "p1"}, "sk": {"S": "a"}, "val": {"N": "1"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p1"}, "sk": {"S": "b"}, "val": {"N": "2"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p2"}, "sk": {"S": "c"}, "val": {"N": "3"}},
    )

    import json
    result = cli(
        "dynamodb", "query",
        "--table-name", table,
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"p1"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["Count"] == 2
    sort_keys = sorted(item["sk"]["S"] for item in payload["Items"])
    assert sort_keys == ["a", "b"]
    for item in payload["Items"]:
        assert item["pk"]["S"] == "p1"

    verify = ddb_client.query(
        TableName=table,
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "p1"}},
    )
    assert verify["Count"] == 2