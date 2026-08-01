from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_after_create(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfDesc1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "describe-table", "--table-name", "WfDesc1")
    assert result.returncode == 0
    assert "WfDesc1" in ddb_client.list_tables()["TableNames"]
