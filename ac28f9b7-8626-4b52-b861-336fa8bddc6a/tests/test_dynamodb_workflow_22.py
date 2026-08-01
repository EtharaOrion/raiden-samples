from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_list_attribute(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf23Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf23Table",
                 "--item", '{"pk":{"S":"l1"},"items":{"L":[{"S":"a"},{"S":"b"}]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf23Table", Key={"pk": {"S": "l1"}})
    assert from_item(resp["Item"])["items"] == ["a", "b"]
