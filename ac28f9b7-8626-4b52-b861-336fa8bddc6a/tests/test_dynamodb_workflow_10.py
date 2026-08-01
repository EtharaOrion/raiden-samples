from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_listtables_membership_after_put(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf11Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf11Table",
                 "--item", '{"pk":{"S":"m1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf11Table" in ddb_client.list_tables()["TableNames"]
