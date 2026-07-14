from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_returns_seeded_item(cli, ddb_client):
    table = "GetItemHappy"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"pk": {"S": "item-1"}, "n": {"N": "42"}, "s": {"S": "hello"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"item-1"}}',
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out["Item"]["pk"]["S"] == "item-1"
    assert out["Item"]["n"]["N"] == "42"
    assert out["Item"]["s"]["S"] == "hello"

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item-1"}})
    assert resp["Item"]["n"]["N"] == "42"