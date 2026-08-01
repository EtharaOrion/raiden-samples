from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_exists_missing_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf47",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf47",
                 "--item", '{"pk":{"S":"nope"}}',
                 "--condition-expression", "attribute_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    assert "Item" not in ddb_client.get_item(TableName="Wf47", Key={"pk": {"S": "nope"}})
