from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_empty_then_seed(cli, ddb_client):
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    ddb_client.create_table(
        TableName="Wf19Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf19Table",
                 "--item", '{"pk":{"S":"seed"}}')
    assert result.returncode == 0
    assert "Wf19Table" in ddb_client.list_tables()["TableNames"]
