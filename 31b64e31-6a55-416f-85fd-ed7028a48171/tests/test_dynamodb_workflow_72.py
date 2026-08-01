from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_puts_condition_second_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf73Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf73Tbl",
                 "--item", '{"pk":{"S":"x"},"v":{"N":"1"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf73Tbl",
                 "--item", '{"pk":{"S":"x"},"v":{"N":"2"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf73Tbl", Key={"pk": {"S": "x"}})
    assert resp["Item"]["v"]["N"] == "1"
