from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_two_creates_both_present(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfBothX",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "WfBothY",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    names = ddb_client.list_tables()["TableNames"]
    assert "WfBothX" in names
    assert "WfBothY" in names
