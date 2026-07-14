from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_query_returns_items_by_partition_key(cli, ddb_client):
    table = "QueryTable1"
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
        Item={"pk": {"S": "p1"}, "sk": {"S": "s1"}, "val": {"N": "10"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p1"}, "sk": {"S": "s2"}, "val": {"N": "20"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "p2"}, "sk": {"S": "s1"}, "val": {"N": "30"}},
    )

    result = cli(
        "dynamodb", "query",
        "--table-name", table,
        "--key-condition-expression", "pk = :v",
        "--expression-attribute-values", '{":v":{"S":"p1"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["Count"] == 2
    sks = sorted(item["sk"]["S"] for item in payload["Items"])
    assert sks == ["s1", "s2"]

    verify = ddb_client.query(
        TableName=table,
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "p1"}},
    )
    assert verify["Count"] == 2