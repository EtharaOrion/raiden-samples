from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_returns_seeded_item(cli, ddb_client):
    table = "GetItemTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "abc"}, "n": {"N": "5"}, "s": {"S": "hello"}},
    )

    result = cli(
        "dynamodb",
        "get-item",
        "--table-name",
        table,
        "--key",
        '{"pk":{"S":"abc"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    item = payload["Item"]
    assert item["pk"] == {"S": "abc"}
    assert item["n"] == {"N": "5"}
    assert item["s"] == {"S": "hello"}

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "abc"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["n"] == {"N": "5"}