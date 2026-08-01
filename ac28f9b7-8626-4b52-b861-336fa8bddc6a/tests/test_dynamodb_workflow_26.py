from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_map_attribute(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf27Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "describe-limits")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf27Table",
                 "--item", '{"pk":{"S":"mp1"},"m":{"M":{"inner":{"S":"val"}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf27Table", Key={"pk": {"S": "mp1"}})
    assert from_item(resp["Item"])["m"] == {"inner": "val"}
