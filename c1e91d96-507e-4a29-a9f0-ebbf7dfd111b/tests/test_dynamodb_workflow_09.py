from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfDescM1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "describe-table", "--table-name", "WfDescMNope")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
