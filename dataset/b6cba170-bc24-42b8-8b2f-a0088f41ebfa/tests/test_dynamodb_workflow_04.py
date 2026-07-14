from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFExistsForNeg",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "get-item", "--table-name", "WFNoSuchTable123",
                 "--key", '{"pk":{"S":"z"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
