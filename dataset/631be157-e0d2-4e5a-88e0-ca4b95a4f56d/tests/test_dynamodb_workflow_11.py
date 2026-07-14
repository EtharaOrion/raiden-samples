from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_creates_listable_and_readable(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf_ListRead",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    assert "Wf_ListRead" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf_ListRead",
                 "--item", '{"pk":{"S":"lr1"},"score":{"N":"42"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf_ListRead", Key={"pk": {"S": "lr1"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["score"] == 42
