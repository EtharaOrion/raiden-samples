from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_success_new_key(cli, ddb_client):
    ddb_client.create_table(
        TableName="Wf16Table",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "list-tables")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf16Table",
                 "--item", '{"pk":{"S":"cs1"},"v":{"S":"ok"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf16Table", Key={"pk": {"S": "cs1"}})
    assert from_item(resp["Item"])["v"] == "ok"
