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

These are all implemented on the BlueMix OpenWhisk platform in
python.

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

* signup for an IBM Cloud account -
  https://console.bluemix.net/dashboard/apps
* allocate a personal access token in github

```bash
# build a package to store github creds
bx wsk package bind /whisk.system/github GitHubWebHook --param-file github.json

```

### ack-github ###

```bash
# create a trigger based on github webhook
bx wsk trigger create GitHubWebHookIssues --feed \
    GitHubWebHook/webhook --param events issues

# create an action for ack-github
bx wsk action update ack-github actions/ack-github.py \
   --param github_creds GitHubWebHook --docker sdague/python3action

# connect trigger to action with a rule
bx wsk rule update GitHubWebHookIssues ack-github

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

Once you've done that you can run the following:

```bash
# create a cron trigger for sending emails
bx wsk trigger create time-for-github-email --feed /whisk.system/alarms/alarm -p cron '0 5 * * 6'

# create an action for send-email
bx wsk action update send-email actions/send-email.py -P mail.json \
    --param github_creds GitHubWebHook --docker sdague/python3action

# connect trigger to action
bx wsk rule update SendGithubEmail time-for-github-email send-email
```

You can test this with:

```bash
bx wsk invoke --blocking send-email
```
