import json
import random

from locustio.common_utils import init_logger, jira_measure, run_as_specific_user
from locustio.jira.requests_params import jira_datasets

jira_dataset = jira_datasets()

HEADERS = {
    # Required to get POSTs to work.
    "X-Atlassian-Token": "no-check",
}
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"


logger = init_logger(app_type='jira')


@jira_measure("security_for_jira_locust_app_specific_action_load_scan")
@run_as_specific_user(username=ADMIN_USER, password=ADMIN_PASSWORD)
def get_issue_scan(locust):
    """Get the scan result for a single issue."""
    issue_key = random.choice(jira_dataset['issues'])[0]
    reviewed = False

    response = locust.get(
        url=f'/rest/security/latest/scan/issue/{issue_key}'
            f'?reviewed={reviewed}',
        catch_response=True,
        headers=HEADERS)

    content = response.content.decode('utf-8')
    scan_dto = json.loads(content)

    assert "scanState" in scan_dto, f"Scan state not in scan report response: {scan_dto}"
    assert "upToDateContent" in scan_dto, f"Scan state up-to-date content not in scan report response: {scan_dto}"
    assert "upToDateSettings" in scan_dto, f"Scan state up-to-date settings not in scan report response: {scan_dto}"


@jira_measure("security_for_jira_locust_app_specific_action_scan_issue")
@run_as_specific_user(username=ADMIN_USER, password=ADMIN_PASSWORD)
def scan_issue(locust):
    """Schedule a scan """
    issue_key = random.choice(jira_dataset['issues'])[0]

    response = locust.post(
        url='/rest/security/latest/scan/issue'
            f'?key={issue_key}',
        catch_response=True,
        headers=HEADERS)

    content = response.content.decode('utf-8')
    scan_dto = json.loads(content)

    assert "scanState" in scan_dto, f"Scan state not in scan report response: {scan_dto}"
    assert scan_dto["scanState"] == "SCHEDULED", \
        f"Scan state is {scan_dto['scanState']}, expected Scheduled. DTO: {scan_dto}"

    assert "upToDateContent" in scan_dto, f"Scan state liveness not in scan report response: {scan_dto}"
    assert scan_dto["upToDateContent"], f"Scan state is not up to date with regard to content. DTO: {scan_dto}"

    assert "upToDateSettings" in scan_dto, f"Scan state up-to-date settings not in scan report response: {scan_dto}"
    assert scan_dto["upToDateSettings"], f"Scan state is not up to date with regard to settings. DTO: {scan_dto}"
