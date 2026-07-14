from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_update_getitem(cli, ddb_client, tmp_path):
    from _ddb_http import from_item
    ddb_client.create_table(
        TableName="WfTblUpdate",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfTblUpdate",
                 "--item", '{"pk":{"S":"u1"},"status":{"S":"old"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "update-item", "--table-name", "WfTblUpdate",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET #s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"new"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTblUpdate", Key={"pk": {"S": "u1"}})
    assert from_item(resp["Item"])["status"] == "new"
