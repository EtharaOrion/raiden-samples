from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multiple_condition_puts_sequence(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_mcps1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for k in ("x", "y", "z"):
        result = cli("dynamodb", "put-item", "--table-name", "Tbl_mcps1",
                     "--item", '{"pk":{"S":"%s"},"v":{"S":"v_%s"}}' % (k, k),
                     "--condition-expression", "attribute_not_exists(pk)")
        assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_mcps1",
                 "--item", '{"pk":{"S":"x"},"v":{"S":"dup"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_mcps1", Key={"pk": {"S": "x"}})
    assert from_item(resp["Item"]) == {"pk": "x", "v": "v_x"}
