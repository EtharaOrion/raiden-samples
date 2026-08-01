from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_missing_after_recreate_gone(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf59",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-table", "--table-name", "Wf59")
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf59", "--key", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
