from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_readback(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfPutGet",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfPutGet",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"}}')
    assert result.returncode == 0
    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="WfPutGet", Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    assert from_item(resp["Item"]) == {"pk": "a1", "n": 5}
