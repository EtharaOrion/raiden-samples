from _ddb_http import to_item, from_item, to_av, from_av


def test_query_partition_key_condition(cli, ddb_client):
    import json

    table = "QueryTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "N"},
        ],
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "grp1"}, "sk": {"N": "1"}, "val": {"S": "a"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "grp1"}, "sk": {"N": "2"}, "val": {"S": "b"}},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "grp2"}, "sk": {"N": "1"}, "val": {"S": "c"}},
    )

    result = cli(
        "dynamodb",
        "query",
        "--table-name",
        table,
        "--key-condition-expression",
        "pk = :p",
        "--expression-attribute-values",
        '{":p":{"S":"grp1"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["Count"] == 2
    returned_sks = sorted(item["sk"]["N"] for item in payload["Items"])
    assert returned_sks == ["1", "2"]
    for item in payload["Items"]:
        assert item["pk"]["S"] == "grp1"

    verify = ddb_client.query(
        TableName=table,
        KeyConditionExpression="pk = :p",
        ExpressionAttributeValues={":p": {"S": "grp1"}},
    )
    assert verify["Count"] == 2