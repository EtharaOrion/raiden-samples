from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_via_cli_ddb_verify(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_pgv1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_pgv1",
                 "--item", '{"pk":{"S":"cli1"},"count":{"N":"7"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_pgv1",
                 "--key", '{"pk":{"S":"cli1"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_pgv1", Key={"pk": {"S": "cli1"}})
    assert from_item(resp["Item"]) == {"pk": "cli1", "count": 7}
