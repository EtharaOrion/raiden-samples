from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_non_key_attr_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfQueryBad",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="WfQueryBad", Item={"pk": {"S": "p1"}, "other": {"S": "z"}})
    result = cli("dynamodb", "query", "--table-name", "WfQueryBad",
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"z"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
