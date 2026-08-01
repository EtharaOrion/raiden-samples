from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_scan_returns_all_items(cli, ddb_client):
    table = "ScanTbl"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "a"}, "n": {"N": "1"}})
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "b"}, "n": {"N": "2"}})
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "c"}, "n": {"N": "3"}})

    result = cli("dynamodb", "scan", "--table-name", table)
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    pks = {item["pk"]["S"] for item in payload["Items"]}
    assert pks == {"a", "b", "c"}
    assert payload["Count"] == 3