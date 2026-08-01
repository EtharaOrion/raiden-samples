from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_multiple_types_verify(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf79Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf79Table",
                 "--item", '{"pk":{"S":"mt1"},"s":{"S":"str"},"n":{"N":"7"},"b":{"BOOL":true},"l":{"L":[{"N":"1"}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf79Table", Key={"pk": {"S": "mt1"}})
    item = from_item(resp["Item"])
    assert item["s"] == "str" and item["n"] == 7 and item["b"] is True and item["l"] == [1]
