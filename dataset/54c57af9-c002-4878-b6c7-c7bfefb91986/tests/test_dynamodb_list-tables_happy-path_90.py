from _ddb_http import to_item, from_item, to_av, from_av


import json

def test_list_tables_returns_created_tables(cli, ddb_client):
    ddb_client.create_table(
        TableName="TblOne",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.create_table(
        TableName="TblTwo",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    names = payload["TableNames"]
    assert "TblOne" in names
    assert "TblTwo" in names

    server_names = ddb_client.list_tables()["TableNames"]
    assert "TblOne" in server_names
    assert "TblTwo" in server_names