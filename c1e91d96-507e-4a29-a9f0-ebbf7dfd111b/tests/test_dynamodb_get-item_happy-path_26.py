from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_returns_existing_item(cli, ddb_client):
    table = "GetItemTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "item1"}, "n": {"N": "42"}, "s": {"S": "hello"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", json.dumps({"pk": {"S": "item1"}}),
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    item = payload["Item"]
    assert item["pk"] == {"S": "item1"}
    assert item["n"] == {"N": "42"}
    assert item["s"] == {"S": "hello"}

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    stored = resp.get("Item")
    assert stored is not None
    assert stored["n"] == {"N": "42"}