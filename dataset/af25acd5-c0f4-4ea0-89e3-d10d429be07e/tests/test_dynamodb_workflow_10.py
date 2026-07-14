from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attribute_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="QueryBadTbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")

    result = cli("dynamodb", "put-item", "--table-name", "QueryBadTbl",
                 "--item", '{"pk":{"S":"q1"},"other":{"S":"z"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "query", "--table-name", "QueryBadTbl",
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"z"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
