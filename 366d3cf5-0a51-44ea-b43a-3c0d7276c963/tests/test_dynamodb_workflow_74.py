from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_delete_condition_fail_keeps(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf75",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf75",
                 "--item", '{"pk":{"S":"k"},"s":{"S":"live"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf75",
                 "--key", '{"pk":{"S":"k"}}',
                 "--condition-expression", "s = :w",
                 "--expression-attribute-values", '{":w":{"S":"dead"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    assert from_item(ddb_client.get_item(TableName="Wf75", Key={"pk": {"S": "k"}})["Item"]) == {"pk": "k", "s": "live"}
