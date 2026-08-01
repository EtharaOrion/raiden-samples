from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_list_verifies_existence(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf40Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf40Table",
                 "--item", '{"pk":{"S":"pl1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf40Table" in ddb_client.list_tables()["TableNames"]
    resp = ddb_client.get_item(TableName="Wf40Table", Key={"pk": {"S": "pl1"}})
    assert "Item" in resp
