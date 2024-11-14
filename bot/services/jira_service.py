import os
from jira import JIRA
from typing import Tuple

class JiraService:
    def __init__(self):
        self.jira = JIRA(
            server=os.getenv('JIRA_URL'),
            basic_auth=(os.getenv('JIRA_USER'), os.getenv('JIRA_TOKEN'))
        )

    def update_task_status(self, task_key: str, assignee: str) -> Tuple[bool, str]:
        try:
            issue = self.jira.issue(task_key)
            
            # Update assignee
            issue.update(assignee={'name': assignee})
            
            # Update status to "Review"
            transitions = self.jira.transitions(issue)
            review_transition = next(
                (t for t in transitions if t['name'].lower() == 'review'),
                None
            )
            
            if review_transition:
                self.jira.transition_issue(issue, review_transition['id'])
                return True, "Jira task updated successfully"
            else:
                return False, "Review transition not found"
                
        except Exception as e:
            return False, f"Error updating Jira task: {str(e)}" 