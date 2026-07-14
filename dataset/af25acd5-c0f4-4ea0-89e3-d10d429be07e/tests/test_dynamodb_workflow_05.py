from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_condition_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="CondDelTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")

    result = cli("dynamodb", "put-item", "--table-name", "CondDelTbl",
                 "--item", '{"pk":{"S":"c1"},"status":{"S":"active"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "delete-item", "--table-name", "CondDelTbl",
                 "--key", '{"pk":{"S":"c1"}}',
                 "--condition-expression", "#s = :v",
                 "--expression-attribute-names", '{"#s":"status"}',
                 "--expression-attribute-values", '{":v":{"S":"inactive"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="CondDelTbl", Key={"pk": {"S": "c1"}})
    assert "Item" in resp
