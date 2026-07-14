from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_getitem_readback(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf_PutGet",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf_PutGet",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"},"s":{"S":"hi"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf_PutGet", Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    item = from_item(resp["Item"])
    assert item["pk"] == "a1"
    assert item["n"] == 5
    assert item["s"] == "hi"
