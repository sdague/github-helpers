#
#
# main() will be invoked when you Run This Action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#

import github
from openwhisk import openwhisk as ow


def thank_you(params):
    p = ow.params_from_pkg(params["github_creds"])
    g = github.Github(p["accessToken"], per_page=100)

    issue = str(params["issue"]["number"])


    repo = g.get_repo(params["repository"]["full_name"])
    name = params["sender"]["login"]
    user_issues = repo.get_issues(creator=name)
    num_issues = len(list(user_issues))

    issue = repo.get_issue(params["issue"]["number"])

    if num_issues < 3:
        comment = """

I really appreciate finding out how people are using this software in
the wide world, and people taking the time to report issues when they
find them.

I only get a chance to work on this project on the weekends, so please
be patient as it takes time to get around to looking into the issues
in depth.

"""
    else:
        comment = """
Thanks very much for reporting an issue. Always excited to see
returning contributors with %d issues created . This is a spare time
project so I only tend to get around to things on the weekends. Please
be patient for me getting a chance to look into this.
""" % num_issues

    issue.create_comment(comment)


def main(params):
    action = params["action"]
    issue = str(params["issue"]["number"])
    if action == "opened":
        thank_you(params)
        return { 'message': 'Success' }
    return { 'message': 'Skipped invocation for %s' % action }
