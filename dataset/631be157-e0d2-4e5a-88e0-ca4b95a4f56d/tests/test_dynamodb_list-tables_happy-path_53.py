from _ddb_http import to_item, from_item, to_av, from_av


import json

def test_list_tables_returns_created_table(cli, ddb_client):
    ddb_client.create_table(
        TableName="MyListTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert "MyListTbl" in payload["TableNames"]
    assert "MyListTbl" in ddb_client.list_tables()["TableNames"]