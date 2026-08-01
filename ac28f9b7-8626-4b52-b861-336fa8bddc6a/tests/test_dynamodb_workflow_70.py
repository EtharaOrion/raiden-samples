from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_list_after_multiple_puts_same_table(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf71Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for i in range(3):
        result = cli("dynamodb", "put-item", "--table-name", "Wf71Table",
                     "--item", '{"pk":{"S":"k%d"}}' % i)
        assert result.returncode == 0
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf71Table" in ddb_client.list_tables()["TableNames"]
    resp = ddb_client.get_item(TableName="Wf71Table", Key={"pk": {"S": "k2"}})
    assert "Item" in resp
