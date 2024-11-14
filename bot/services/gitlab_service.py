import os
import gitlab
from typing import Optional, Tuple

class GitLabService:
    def __init__(self):
        self.gl = gitlab.Gitlab(
            os.getenv('GITLAB_URL'),
            private_token=os.getenv('GITLAB_TOKEN')
        )

    def assign_merge_request(self, mr_link: str, assignee_username: str) -> Tuple[bool, str]:
        try:
            # Extract project and MR ID from link
            # Example link: https://gitlab.com/project/repo/-/merge_requests/123
            parts = mr_link.split('/-/merge_requests/')
            if len(parts) != 2:
                return False, "Invalid merge request link format"

            project_path = parts[0].split('gitlab.com/')[1]
            mr_id = int(parts[1])

            project = self.gl.projects.get(project_path)
            mr = project.mergerequests.get(mr_id)
            mr.assignee_id = self.gl.users.list(username=assignee_username)[0].id
            mr.save()

            return True, "Merge request assigned successfully"
        except Exception as e:
            return False, f"Error assigning merge request: {str(e)}"

    def get_mr_title(self, mr_link: str) -> Tuple[bool, Optional[str], str]:
        try:
            parts = mr_link.split('/-/merge_requests/')
            if len(parts) != 2:
                return False, None, "Invalid merge request link format"

            project_path = parts[0].split('gitlab.com/')[1]
            mr_id = int(parts[1])

            project = self.gl.projects.get(project_path)
            mr = project.mergerequests.get(mr_id)
            
            return True, mr.title, "Title retrieved successfully"
        except Exception as e:
            return False, None, f"Error getting MR title: {str(e)}" 