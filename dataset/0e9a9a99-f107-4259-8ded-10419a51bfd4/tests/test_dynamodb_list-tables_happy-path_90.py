from _ddb_http import to_item, from_item, to_av, from_av


import json

def test_list_tables_returns_created_tables(cli, ddb_client):
    ddb_client.create_table(
        TableName="TblA",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.create_table(
        TableName="TblB",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    names = payload["TableNames"]
    assert "TblA" in names
    assert "TblB" in names

    live = ddb_client.list_tables()["TableNames"]
    assert "TblA" in live
    assert "TblB" in live