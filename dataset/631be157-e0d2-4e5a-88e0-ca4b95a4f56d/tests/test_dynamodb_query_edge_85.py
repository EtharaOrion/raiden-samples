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
        Item={"id": {"S": "k1"}, "sk": {"S": "a"}, "val": {"N": "1"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k1"}, "sk": {"S": "b"}, "val": {"N": "2"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k2"}, "sk": {"S": "c"}, "val": {"N": "3"}},
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
    returned_sks = sorted(item["sk"]["S"] for item in payload["Items"])
    assert returned_sks == ["a", "b"]
    for item in payload["Items"]:
        assert item["id"]["S"] == "k1"

    verify = ddb_client.query(
        TableName=table,
        KeyConditionExpression="id = :pk",
        ExpressionAttributeValues={":pk": {"S": "k1"}},
    )
    assert verify["Count"] == 2