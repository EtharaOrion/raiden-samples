from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_query_by_partition_key_returns_matching_items(cli, ddb_client):
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
        Item={"pk": {"S": "p1"}, "sk": {"S": "a"}, "v": {"N": "1"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p1"}, "sk": {"S": "b"}, "v": {"N": "2"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "other"}, "sk": {"S": "c"}, "v": {"N": "3"}},
    )

    result = cli(
        "dynamodb",
        "query",
        "--table-name",
        table,
        "--key-condition-expression",
        "pk = :p",
        "--expression-attribute-values",
        '{":p":{"S":"p1"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["Count"] == 2
    sks = sorted(item["sk"]["S"] for item in payload["Items"])
    assert sks == ["a", "b"]

    verify = ddb_client.query(
        TableName=table,
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "p1"}},
    )
    assert verify["Count"] == 2