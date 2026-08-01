from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_reserved_word_attr_ok(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf77Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf77Table",
                 "--item", '{"pk":{"S":"rw1"},"Status":{"S":"active"},"Size":{"N":"5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf77Table", Key={"pk": {"S": "rw1"}})
    item = from_item(resp["Item"])
    assert item["Status"] == "active" and item["Size"] == 5
