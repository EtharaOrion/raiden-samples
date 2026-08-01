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
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "a"}, "v": {"N": "1"}})
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "b"}, "v": {"N": "2"}})
    ddb_client.put_item(TableName=table, Item={"pk": {"S": "c"}, "v": {"N": "3"}})

    result = cli("dynamodb", "scan", "--table-name", table)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    pks = {item["pk"]["S"] for item in out["Items"]}
    assert pks == {"a", "b", "c"}
    assert out["Count"] == 3