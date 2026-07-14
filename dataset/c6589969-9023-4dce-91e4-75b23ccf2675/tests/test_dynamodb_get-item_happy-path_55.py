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
        Item={"pk": {"S": "item1"}, "name": {"S": "widget"}, "count": {"N": "42"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"pk":{"S":"item1"}}',
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert "Item" in payload
    assert payload["Item"]["pk"] == {"S": "item1"}
    assert payload["Item"]["name"] == {"S": "widget"}
    assert payload["Item"]["count"] == {"N": "42"}

    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "item1"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["name"] == {"S": "widget"}