from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_describe_table_returns_metadata(cli, ddb_client):
    table_name = "DescribeTbl1"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli("dynamodb", "describe-table", "--table-name", table_name)
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    desc = payload["Table"]
    assert desc["TableName"] == table_name
    key_names = {k["AttributeName"]: k["KeyType"] for k in desc["KeySchema"]}
    assert key_names == {"pk": "HASH"}

    assert table_name in ddb_client.list_tables()["TableNames"]