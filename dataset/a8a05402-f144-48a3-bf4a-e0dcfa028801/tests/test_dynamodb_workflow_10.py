from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_non_key_attr_validation(cli, ddb_client, tmp_path):
    table = "WfQueryBad"
    ddb_client.create_table(
        TableName=table,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", table,
                 "--item", '{"pk":{"S":"z1"},"other":{"S":"foo"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", table,
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"foo"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
