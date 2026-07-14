from _ddb_http import to_item, from_item, to_av, from_av


import json


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
        Item={"pk": {"S": "abc"}, "sk": {"S": "1"}, "v": {"N": "10"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "abc"}, "sk": {"S": "2"}, "v": {"N": "20"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "other"}, "sk": {"S": "1"}, "v": {"N": "99"}},
    )

    result = cli(
        "dynamodb",
        "query",
        "--table-name",
        table,
        "--key-condition-expression",
        "pk = :p",
        "--expression-attribute-values",
        '{":p":{"S":"abc"}}',
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out["Count"] == 2
    sks = sorted(item["sk"]["S"] for item in out["Items"])
    assert sks == ["1", "2"]
    for item in out["Items"]:
        assert item["pk"]["S"] == "abc"