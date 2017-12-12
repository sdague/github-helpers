from collections import namedtuple

import requests
import github

from openwhisk import openwhisk as ow

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

def open_issues_report(name, issues):
    html = "<table><tr><th colspan=4>%s open issues</th></tr>\n" % name
    html += "<tr><td width='55%'>Subject</td><td width='20%'>Created</td><td width='20%'>Last Updated</td><td>Comments</td></tr>\n"

    for i in issues:
        html += '<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (
            i.html_url, i.title, i.created_at.strftime("%b %e %Y"),
            i.updated_at.strftime("%b %e %Y"), i.comments)
    html += "</table>\n<p>"
    return html

def find_issues_by_owner(token):
    g = github.Github(token, per_page=100)
    repos = g.get_user().get_repos(type="owner")

    results = list()
    for r in repos:
        issues = r.get_issues()
        if (len(list(issues))):
            report = namedtuple('Report', ['name', 'issues'])
            report.name = r.full_name
            report.issues = issues
            results.append(report)
    return results

def email_report(results):
    html = """<p>
Here is your current report of open github issues for projects
that you are listed as the owner for.
</p>"""

    # optimization, don't do archived projects
    for res in results:
        html += open_issues_report(res.name, res.issues)
    return html

def send_report(email_from, email_to, email_pass, github_token):
    results = find_issues_by_owner(github_token)
    html = email_report(results)
    msg = MIMEText(html, 'html')
    msg['Subject'] = 'Open Github Issues Report'
    msg['From'] = email_from
    msg['To'] = email_to
    # Send the message via our own SMTP server.
    # return { 'message': "Worked! %s" % repos }

    s = smtplib.SMTP('smtp.fastmail.com', 587)
    s.ehlo()
    s.starttls()
    s.login(email_from, email_pass)
    s.send_message(msg)
    s.quit()


def main(params):
    passwd = params['passwd']
    sender = params['sender']
    to = params['to']
    github_token = ow.params_from_pkg(params["github_creds"])['accessToken']

    send_report(sender, to, passwd, github_token)

    return { 'message': "Worked!" }
