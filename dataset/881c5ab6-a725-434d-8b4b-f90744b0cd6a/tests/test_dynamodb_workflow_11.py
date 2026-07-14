from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_conditional_fail(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblL",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblL", Item={"pk": {"S": "k"}, "v": {"S": "keep"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblL",
                 "--key", '{"pk":{"S":"k"}}',
                 "--condition-expression", "v = :expected",
                 "--expression-attribute-values", '{":expected":{"S":"other"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblL", Key={"pk": {"S": "k"}})
    assert from_item(resp["Item"])["v"] == "keep"
