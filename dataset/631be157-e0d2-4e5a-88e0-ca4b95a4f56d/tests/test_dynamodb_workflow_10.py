from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_non_key_validation_error(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf_QueryVal",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    result = cli("dynamodb", "put-item", "--table-name", "Wf_QueryVal",
                 "--item", '{"pk":{"S":"q1"},"other":{"S":"z"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "query", "--table-name", "Wf_QueryVal",
                 "--key-condition-expression", "other = :v",
                 "--expression-attribute-values", '{":v":{"S":"z"}}')
    assert result.returncode != 0
    assert "ValidationException" in result.stderr
