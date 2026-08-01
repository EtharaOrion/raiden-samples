from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_putitem_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf5",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf5Missing",
                 "--item", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
