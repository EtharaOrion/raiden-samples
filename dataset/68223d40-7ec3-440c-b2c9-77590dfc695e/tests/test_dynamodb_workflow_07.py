from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attr_validation(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfQuery2",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfQuery2", Item={"pk": {"S": "q1"}, "color": {"S": "red"}})
    result = cli("dynamodb", "query", "--table-name", "WfQuery2",
                 "--key-condition-expression", "color = :v",
                 "--expression-attribute-values", '{":v":{"S":"red"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
