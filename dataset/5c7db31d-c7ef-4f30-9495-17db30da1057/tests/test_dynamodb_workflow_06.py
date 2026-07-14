from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_item_condition_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblF",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblF", Item={"pk": {"S": "row2"}, "v": {"S": "keep"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfTblF",
                 "--key", '{"pk":{"S":"row2"}}',
                 "--condition-expression", "v = :v",
                 "--expression-attribute-values", '{":v":{"S":"nomatch"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTblF", Key={"pk": {"S": "row2"}})
    assert "Item" in resp
    assert from_item(resp["Item"])["v"] == "keep"
