from collections import namedtuple

import requests
import github

from openwhisk import openwhisk as ow

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

def issues_report(name, issues):
    html = "<table><tr><th colspan=5>%s open issues</th></tr>\n" % name
    html += "<tr><td width='40%'>Subject</td>"
    html += "<td width='15%'>Created</td><td width='15%'>Last Updated</td>"
    html += "<td>Comments</td><td>Labels</td></tr>\n"

    for x, i in enumerate(issues):
        # basic stiple for readability
        if x % 2:
            bgcolor = "#fff"
        else:
            bgcolor = "#ddd"
        html += ('<tr valign="top" bgcolor="%s"><td><a href="%s">%s</a></td><td>%s</td>'
                 '<td>%s</td><td>%s</td><td>%s</td></tr>\n' % (
                     bgcolor,
                     i.html_url,
                     i.title,
                     i.created_at.strftime("%b %e %Y"),
                     i.updated_at.strftime("%b %e %Y"),
                     i.comments,
                     "<br/> ".join([x.name for x in i.labels])))
    html += "</table>\n<p>"
    return html

def find_issues_by_keywords(project, token, keywords):
    g = github.Github(token, per_page=100)
    # TODO(sdague): quoting multi word phrases, and possibly NOTs
    issues = g.search_issues(
        "(%s) repo:%s is:open" % (
            " OR ".join(keywords), project),
        sort="updated",
        order="desc"
    )

    return issues

def email_report(name, keywords, issues):
    html = """<p>
Here is your current report of search for issues based on your
search keywords on %s for: %s.
</p>""" % (name, ", ".join(keywords))
    html += issues_report(name, issues)
    return html

def send_report(email_from, email_to, email_pass, github_token, project, keywords):
    issues = find_issues_by_keywords(project, github_token, keywords)
    html = email_report(project, keywords, issues)
    msg = MIMEText(html, 'html')
    msg['Subject'] = 'Selected github issues for %s' % project
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
    project = params["project"]
    keywords = params["keywords"]

    github_token = ow.params_from_pkg(params["github_creds"])['accessToken']

    send_report(sender, to, passwd, github_token, project, keywords)

    return { 'message': "Worked!" }
