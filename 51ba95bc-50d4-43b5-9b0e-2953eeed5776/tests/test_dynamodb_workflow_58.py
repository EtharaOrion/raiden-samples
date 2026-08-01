from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_before_and_after_overwrite(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_gbao1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_gbao1",
                 "--item", '{"pk":{"S":"ba1"},"v":{"S":"before"}}')
    assert result.returncode == 0
    before = ddb_client.get_item(TableName="Tbl_gbao1", Key={"pk": {"S": "ba1"}})
    assert from_item(before["Item"])["v"] == "before"
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_gbao1",
                 "--item", '{"pk":{"S":"ba1"},"v":{"S":"after"}}')
    assert result.returncode == 0
    after = ddb_client.get_item(TableName="Tbl_gbao1", Key={"pk": {"S": "ba1"}})
    assert from_item(after["Item"])["v"] == "after"
