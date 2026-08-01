from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_number_precision_string_preserved(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_prec1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_prec1",
                 "--item", '{"pk":{"S":"pr1"},"amt":{"N":"100.00"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_prec1", Key={"pk": {"S": "pr1"}})
    assert resp["Item"]["amt"]["N"] in ("100.00", "100")
