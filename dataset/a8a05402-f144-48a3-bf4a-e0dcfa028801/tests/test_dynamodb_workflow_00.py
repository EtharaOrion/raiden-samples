from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_readback(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    table = "WfPutGet"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", table,
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"},"s":{"S":"hi"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName=table, Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    native = from_item(resp["Item"])
    assert native["n"] == 5
    assert native["s"] == "hi"
