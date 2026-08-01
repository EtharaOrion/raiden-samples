from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_before_get_missing_table_still_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf78Real",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf78Real",
                 "--item", '{"pk":{"S":"a"},"v":{"S":"x"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf78Fake",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
