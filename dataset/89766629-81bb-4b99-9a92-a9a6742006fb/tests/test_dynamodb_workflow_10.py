from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_nonkey_attribute_fails(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="WfQueryBad",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "WfQueryBad",
                 "--item", '{"pk":{"S":"z1"},"other":{"S":"vv"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", "WfQueryBad",
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"vv"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
