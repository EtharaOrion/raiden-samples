from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_get_item_consistent_read(cli, ddb_client):
    table = "GetItemConsistentTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(
        TableName=table,
        Item={"id": {"S": "k1"}, "val": {"S": "hello"}, "n": {"N": "7"}},
    )

    result = cli(
        "dynamodb", "get-item",
        "--table-name", table,
        "--key", '{"id":{"S":"k1"}}',
        "--consistent-read",
    )
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["Item"]["id"]["S"] == "k1"
    assert payload["Item"]["val"]["S"] == "hello"
    assert payload["Item"]["n"]["N"] == "7"

    resp = ddb_client.get_item(TableName=table, Key={"id": {"S": "k1"}})
    assert resp.get("Item") is not None
    assert resp["Item"]["val"]["S"] == "hello"