from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_limits_then_list(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf46Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf46Table" in ddb_client.list_tables()["TableNames"]
