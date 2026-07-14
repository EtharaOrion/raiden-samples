from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_query_by_partition_key(cli, ddb_client):
    table = "QueryTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k1"}, "sk": {"S": "a"}, "v": {"S": "one"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k1"}, "sk": {"S": "b"}, "v": {"S": "two"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k2"}, "sk": {"S": "c"}, "v": {"S": "three"}},
    )

    result = cli(
        "dynamodb", "query",
        "--table-name", table,
        "--key-condition-expression", "id = :pk",
        "--expression-attribute-values", '{":pk":{"S":"k1"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["Count"] == 2
    ids = {item["id"]["S"] for item in payload["Items"]}
    assert ids == {"k1"}
    sks = {item["sk"]["S"] for item in payload["Items"]}
    assert sks == {"a", "b"}

    resp = ddb_client.query(
        TableName=table,
        KeyConditionExpression="id = :pk",
        ExpressionAttributeValues={":pk": {"S": "k1"}},
    )
    assert resp["Count"] == 2