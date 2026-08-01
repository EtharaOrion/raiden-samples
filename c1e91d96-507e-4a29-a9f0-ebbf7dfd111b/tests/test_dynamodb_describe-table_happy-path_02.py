from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_describe_table_returns_metadata(cli, ddb_client):
    table_name = "DescribeMe"
    ddb_client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    assert table_name in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "describe-table", "--table-name", table_name)
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    table = payload["Table"]
    assert table["TableName"] == table_name
    key_schema = table["KeySchema"]
    assert {"AttributeName": "pk", "KeyType": "HASH"} in key_schema
    attr_names = [a["AttributeName"] for a in table["AttributeDefinitions"]]
    assert "pk" in attr_names