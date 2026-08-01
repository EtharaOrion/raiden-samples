from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_scan_returns_all_items(cli, ddb_client):
    ddb_client.create_table(
        TableName="ScanTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName="ScanTbl", Item={"pk": {"S": "a"}, "n": {"N": "1"}})
    ddb_client.put_item(TableName="ScanTbl", Item={"pk": {"S": "b"}, "n": {"N": "2"}})
    ddb_client.put_item(TableName="ScanTbl", Item={"pk": {"S": "c"}, "n": {"N": "3"}})

    result = cli("dynamodb", "scan", "--table-name", "ScanTbl")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    assert payload["Count"] == 3
    pks = sorted(item["pk"]["S"] for item in payload["Items"])
    assert pks == ["a", "b", "c"]