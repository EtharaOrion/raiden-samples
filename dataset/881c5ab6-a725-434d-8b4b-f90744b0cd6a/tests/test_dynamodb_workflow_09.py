from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attr_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfTblJ",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfTblJ", Item={"pk": {"S": "z"}, "foo": {"S": "bar"}})
    result = cli("dynamodb", "query", "--table-name", "WfTblJ",
                 "--key-condition-expression", "foo = :v",
                 "--expression-attribute-values", '{":v":{"S":"bar"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
