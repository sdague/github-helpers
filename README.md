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

Coming soon....
