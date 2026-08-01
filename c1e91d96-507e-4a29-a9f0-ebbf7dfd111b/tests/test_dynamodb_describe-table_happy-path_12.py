from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_describe_table_returns_metadata(cli, ddb_client):
    ddb_client.create_table(
        TableName="DescribeMe",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    result = cli("dynamodb", "describe-table", "--table-name", "DescribeMe")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    desc = payload["Table"]
    assert desc["TableName"] == "DescribeMe"
    key_names = [k["AttributeName"] for k in desc["KeySchema"]]
    assert "pk" in key_names
    assert "DescribeMe" in ddb_client.list_tables()["TableNames"]