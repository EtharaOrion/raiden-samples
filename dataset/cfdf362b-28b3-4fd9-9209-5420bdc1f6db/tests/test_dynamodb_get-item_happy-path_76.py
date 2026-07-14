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
        Item={"pk": {"S": "item1"}, "name": {"S": "widget"}, "count": {"N": "7"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"item1"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    item = payload["Item"]
    assert item["pk"]["S"] == "item1"
    assert item["name"]["S"] == "widget"
    assert item["count"]["N"] == "7"