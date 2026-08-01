from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_query_missing_table(cli, ddb_client, tmp_path):
    t = "wf_query_missing_4"
    result = cli("dynamodb", "query", "--table-name", t,
                 "--key-condition-expression", "pk = :v",
                 "--expression-attribute-values", '{":v":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
