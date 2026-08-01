from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_putitem_listtables_readback(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf1Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf1Table",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf1Table", Key={"pk": {"S": "a1"}})
    assert from_item(resp["Item"]) == {"pk": "a1", "n": 5}
