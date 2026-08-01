from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_describe_table_returns_schema(cli, ddb_client):
    ddb_client.create_table(
        TableName="DescTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli("dynamodb", "describe-table", "--table-name", "DescTbl")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    table = out["Table"]
    assert table["TableName"] == "DescTbl"
    key_names = {k["AttributeName"] for k in table["KeySchema"]}
    assert "pk" in key_names

    assert "DescTbl" in ddb_client.list_tables()["TableNames"]