# ⨯post

`⨯post` is a tool designed to help you stay in control of your data, specifically built for three main use cases:
* You fill out a contact form on a website, but the site does not send you an email with a copy of your submission; generally (especially when no response is received), all the information is lost (including the text sent, but also the date, time, etc.).
* You post a comment on a site (for example, YouTube, Facebook...), the comment is initially accepted but later you notice that it has been censored: even though you were careful to be politically correct, you no longer have the details to understand why and have to start over from scratch.

Other possible uses may include:
* `delay-post` : where's the fun of starting a flame war on someone if you were too drunk to even remember it? or maybe you just want to wait until the end of a video before you post a comment that later turns out to be irrelevant : `⨯post` provides a tool just for that (TODO)
* `no-post`: you feel strongly about some content published on a website that does not allow posting comments (typically, this is very frequent on government media) : `⨯post` can provide a work-around (TODO)
* `mod-post`: run a regex or any other program on your content before it is posted: this may include things like automated spell corrections, e-mail or password obfuscation, etc.

## How It Works

`⨯post` creates a [proxy server](https://en.wikipedia.org/wiki/Proxy) through which your internet traffic passes; for privacy and performance reasons, this proxy is **local** (on your machine or local network). This component of `⨯post` (which is **free, open-source, and open** to the public) has a simple interface that allows you to:
* view the data you have sent to third parties
* manage the filtering of this data (i.e., ignore certain websites) and what is logged (by default, passwords are not recorded, phone numbers are obfuscated)
* depending on the configuration, `⨯post` can act as a browsing history (particularly useful if you use the same proxy for multiple clients)
* publish all or part of a post on `<somewhere>`, either publicly or semi-privately, indicating the reason for republishing (for example, "this content was censored"). Republishing is subject to a subscription with a pay-what-you-can model (the minimum amount to cover expenses: $7/year, which is less than 2 cents/day); at any time, you can choose to delete your comment's copy.

Ultimately, `⨯post` can be used to generate statistics on websites that censor user content, as well as the proportion of content that caused the censorship.

## Installation

### Local proxy

* call `./run.sh` in the project root
* Configure your browser to use 127.0.0.1:8080 as HTTP and HTTPS proxy
* Go to http://mitm.it and download the certificate (it is generated locally)
* Install certificate:
    * Firefox: Settings → Privacy & Security → Certificates → View Certificates → Authorities → Import
    * Chrome / system-wide:
        * macOS: add to Keychain and mark as “Always Trust”
        * Linux: place in /usr/local/share/ca-certificates/ and run update-ca-certificates
        * Windows: import into “Trusted Root Certification Authorities”
* Visit http://localhost:12345/ to view your post history and do the chosen action (delete, re-publish, etc..)
    * Use http://your.ip.address:12345/test to verify everything works as expected (caveat: some browsers like Firefox do not use the configured proxy for local addresses)

### Alterntaive: browser extension

* call `./run.sh` in the project root
* visit http://172.16.100.11:12345/about for further instructions

Note: this is untested!

## Project stucture
```
xpot/
├── app/
│   ├── __init__.py
│   ├── main.py          # Quart app entrypoint
│   ├── db.py            # DB + writer
│   ├── ingest.py        # websocket ingestion
│   ├── api.py           # HTTP routes
│   ├── stream.py        # WS broadcast
│   └── templates/
│       └── *.html       # HTML templates
│
├── proxy/
│   ├── config.json      # filters by protocol, URL, field name ; obfuscation parameters
│   └── gather.py        # mitmproxy script
│
├── data/
│   └── traffic.db       # sqlite database with the captured data
│
├── requirements.txt
└── run.sh               # script to start the service
```

## TODO

* per-URL fieldname regex rules (and scripts) ; problem with current field name and content rules (ie. passwords are saved)
* shared repository for site-specific regex and scripts (similar to piHole, OctoPrint..)
* user authentication
* `republish` (re-post to an external "neutral" service)
* `report for review` (we can't really expect the end-user to tweak a regex and form rules)
* automatic buffer and auto-delete (after a set time) content that is neither explicitly rejected as noise or explicitly treated as relevant
* save "protect post" in database ; document the feature

## Success stories

### Retrieved content

While working on `⨯post` with ChatGPT[^chatgpt_censoring], one of my prompts was censored for "maybe violating the terms": <i>"tasting is not seeing, you fool"</i> ; this sort of mishaps happens quite often when one is being a smart-ass with LLMs XD

[^chatgpt_censoring]: I was actually parsing the traffic *back* to the user because I also experienced (on **very rare** occasions) that ChatGPT would censor an entire conversation with just the wrong prompt...

### Traffic awareness

When using the proxy, it's quite scary to see how many websites generate traffic when they're supposedly idle in a tab somewhere in the background...

When working on the ChatGPT response parsing above, I realized how much redundant data is sent and this freaked me out.

## Third-party references

* https://www.youtube.com/watch?v=hMiVZoFtH6s "Reddit can't have people recording all of the admin/moderator manipulation."
* Human Rights Watch

## Implementation status of `website_handlers`
```
Y: yes
P: partial
W: Work-in-progress
N: no
n/a: irrelevant (does not apply)
```

|Website/Service   | in[^in] | out[^out] |
|------------------|---------|-----------|
|Youtube           |    N    |    Y      |
|ChatGPT           |    W    |    W      |

[^in]: traffic from the service to the user
[^out]: traffic from the user to the remote service
