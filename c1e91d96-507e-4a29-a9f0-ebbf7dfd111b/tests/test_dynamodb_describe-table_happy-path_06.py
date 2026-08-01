from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_describe_table_returns_metadata(cli, ddb_client):
    ddb_client.create_table(
        TableName="DescMe",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli("dynamodb", "describe-table", "--table-name", "DescMe")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    table = payload["Table"]
    assert table["TableName"] == "DescMe"
    key_attrs = {k["AttributeName"] for k in table["KeySchema"]}
    assert "pk" in key_attrs

    assert "DescMe" in ddb_client.list_tables()["TableNames"]