# Github Helpers #

## Background ##

If you are like me, you have accumulated a non trivial number of
personal open source repositories on github over the years. A bunch of
them are at very low levels of maintenance. Some of them do get PRs or
Issues from time to time, and it is often weeks to months before ever
looking at those.

After seeing this tweet from Jessie Frazelle -
https://twitter.com/jessfraz/status/930148430298611713 I wondered the
ways I could do better with a little bot automation. Serverless makes
for an ideal platform for this, because many of these operations are
really just a couple of seconds of processing.

These are all implemented on the IBM Cloud Functions platform (based
on Apache OpenWhisk) in python.

## Scripts ##

### ack-github ###

This is designed to provide an auto response to newly openned
issues. The idea being to just warn folks that I'm not likely to look
at it until the weekend, at best. It also gives a different message if
the user in question hasn't created more than 1 issue before on this
project.

A new user to your project is probably most likely to misunderstand
why responses come late.

### send-email ###

This uses the cron facility in openwhisk to send an email of all the
open issues on all projects you own. For me, this is scheduled to run
at 5am on Saturday morning, as Saturday mornings before the rest of my
family wakes up are very good times to process things like this.

## Installation ##

### Prereqs ###

* signup for an IBM Cloud Functions account -
  https://console.bluemix.net/openwhisk/ (a Lite account will be
  sufficient for any of these actions)
* allocate a personal access token for the github API -
  https://github.com/settings/tokens
* put this access token into a github.json file like such:

```json
{
    "username": "<youruser>",
    "repository": "<youruser>/<a repo>",
    "accessToken": "<personal access token>"
}
```

The repository is important because the builtin github system actions
do the round trip to the github API and actually create the webhook
definitions in github for you. This has to be done at a repo level.

```bash
# build a package to store github creds
bx wsk package bind /whisk.system/github GitHubWebHook --param-file github.json

export WHISK_IMAGE="sdague/python3action"
```

**Note:** these actions need a custom docker image because they need
libraries beyond what's included in the base
``openwhisk/python3action``. I've got a docker image at
``sdague/python3action`` with those additions.

You can also rebuild it easily by looking in the ``docker/`` directory
and running the ``./buildAndPush.sh`` script. I make no guaruntees on
the contents of my image, so if you are going to run with this long
term, it's best to replace the image with your own.


### ack-github ###

```bash
# create a trigger based on github webhook
bx wsk trigger create GitHubWebHookIssues --feed \
    GitHubWebHook/webhook --param events issues

# create an action for ack-github
bx wsk action update ack-github actions/ack-github.py \
   --param github_creds GitHubWebHook --docker $WHISK_IMAGE

# connect trigger to action with a rule
bx wsk rule update SendGitHubAck GitHubWebHookIssues ack-github

```

### send-email ###

There is no built in email system in openwhisk, as such you need to
use an external system. I use fastmail.fm for personal email, which
allows you to provision per application credentials (easy to track and
revoke later if they leak).

First create a ``mail.json`` file with the following content:

```json
{
    "sender": "<fastmail account address>",
    "to": "<email to send to>",
    "passwd": "<app password>"
}

```

We will be reusing the personal access token from the ack-github
action. Given that this is a query only activity, it shouldn't need
any other permissions.

Once you've done that you can run the following:

```bash
# create a cron trigger for sending emails
bx wsk trigger create time-for-github-email \
    --feed /whisk.system/alarms/alarm -p cron '0 5 * * 6'

# create an action for send-email
bx wsk action update send-email actions/send-email.py -P mail.json \
    --param github_creds GitHubWebHook --docker $WHISK_IMAGE

# connect trigger to action
bx wsk rule update SendGithubEmail time-for-github-email send-email
```

You can test this with:

```bash
bx wsk action invoke --blocking send-email
```

That should send you an html email to the address you specified.

### watched-keywords ###

This is a different slice of the send-email script. For large projects
that you might be involved in, looking at the whole issue queue is
overwhelming. However, there might be a few topics that you feel like
you have deep experience in, that you want to know if there are open
issues.

This builds a search query that you can run periodically for open
issues, and get that collection emailed to you. You can probably at
least triage them.

First create a ``watched.json`` file with the following content:

```json
{
    "sender": "<fastmail account address>",
    "to": "<email to send to>",
    "passwd": "<app password>",
    "project": "<owner/repo>",
    "keywords": ["<keyword1>", "<keyword2>", ...]
}

```

We will be reusing the personal access token from the ack-github
action. Given that this is a query only activity, it shouldn't need
any other permissions.

Once you've done that you can run the following:

```bash
# create a cron trigger for running this action
bx wsk trigger create time-for-watched-email \
    --feed /whisk.system/alarms/alarm -p cron '0 5 * * 6'

# create an action for watched-keywords
bx wsk action update watched-keywords actions/watched-keywords.py -P watched.json \
    --param github_creds GitHubWebHook --docker $WHISK_IMAGE

# connect trigger to action
bx wsk rule update SendWatchedEmail time-for-watched-email watched-keywords
```

You can test this with:

```bash
bx wsk action invoke --blocking watched-keywords
```

That should send you an html email to the address you specified.
