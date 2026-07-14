from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_overwrite_get(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblOver",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblOver",
                 "--item", '{"pk":{"S":"o1"},"v":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTblOver",
                 "--item", '{"pk":{"S":"o1"},"v":{"N":"99"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblOver", Key={"pk": {"S": "o1"}})
    assert from_item(resp["Item"])["v"] == 99
