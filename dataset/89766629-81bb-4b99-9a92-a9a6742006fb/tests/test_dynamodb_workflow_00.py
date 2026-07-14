from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_getitem_readback(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfReadback",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfReadback",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfReadback", Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    assert from_item(resp["Item"]) == {"pk": "a1", "n": 5}
