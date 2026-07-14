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
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "p1"}, "sk": {"S": "a"}, "v": {"N": "1"}})
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "p1"}, "sk": {"S": "b"}, "v": {"N": "2"}})
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "p2"}, "sk": {"S": "a"}, "v": {"N": "3"}})

    result = cli(
        "dynamodb", "query",
        "--table-name", table,
        "--key-condition-expression", "pk = :pkval",
        "--expression-attribute-values", '{":pkval":{"S":"p1"}}',
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out["Count"] == 2
    sks = sorted(item["sk"]["S"] for item in out["Items"])
    assert sks == ["a", "b"]
    for item in out["Items"]:
        assert item["pk"]["S"] == "p1"