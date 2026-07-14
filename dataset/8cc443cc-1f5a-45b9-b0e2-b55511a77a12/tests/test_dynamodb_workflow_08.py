from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_conditional_fail_unchanged(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfCondPutTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )

    result = cli("dynamodb", "put-item", "--table-name", "WfCondPutTbl",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"orig"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "WfCondPutTbl",
                 "--item", '{"pk":{"S":"c1"},"v":{"S":"changed"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    resp = ddb_client.get_item(TableName="WfCondPutTbl", Key={"pk": {"S": "c1"}})
    assert from_item(resp["Item"])["v"] == "orig"
