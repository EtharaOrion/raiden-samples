from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_readback(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf1Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf1Tbl",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"7"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf1Tbl", Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    assert resp["Item"]["n"] == {"N": "7"}
