from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_consistent_read(cli, ddb_client):
    table = "ConsistentReadTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k1"}, "val": {"S": "hello"}, "n": {"N": "42"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"id":{"S":"k1"}}',
        "--consistent-read",
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    item = payload["Item"]
    assert item["id"]["S"] == "k1"
    assert item["val"]["S"] == "hello"
    assert item["n"]["N"] == "42"

    resp = ddb_client.get_item(TableName=table, Key={"id": {"S": "k1"}})
    stored = resp.get("Item")
    assert stored is not None
    assert stored["val"]["S"] == "hello"
    assert stored["n"]["N"] == "42"