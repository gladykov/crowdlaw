# Crowd Law

<p align="center">
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

# Introduction

## What is this?

Tool to collaboratively create law, so anybody can do it. You can write new and edit existing documents, and you can use it for any other purpose. In other words - Git addon.

## Why ?

In 2021 there is no good tool, to write documents by many people. Google Docs and Wiki does not provide good mechanisms for tracking and approving changes, which is crucial when creating transparent law.
Computer programmers for a long time know benefits which come with Git system, but it is too complicated for non-technical person. This is why UI was made as easy as possible, to allow everybody use power of Git.

## How ?

You edit all documents locally, and when you are ready you send changes to one of public servers. As they have tools, allowing to review, discuss and accept proposed changes, all review process is done on public server.

# Installation

[Download one of install packages for your system](https://github.com/gladykov/crowdlaw/releases)

Install and start using - app should be self-explanatory. If it is not, there is always room for improvement.

## Why there is no PyPi module?

App is intended for people not familiar with those technologies and installer is crucial, this is why only single distribution channel, to make life easier. Still you can clone this repo, install requirements and run through `python -m src.main` 
But if there will be additional benefit from PyPi package, I assume I can add in the future.

## Example project

https://gitlab.com/gladykov/example-project-for-crowd-law

# I found an issue!

Great, please let me know:
[Fill Gitlab issue](https://gitlab.com/gladykov/crowdlaw/-/issues/new)
or drop me an email: gladykov gmail com

# Documentation

Does not exist (yet)

# Contribution

There is still so much work to be done. From testing, translations, code review, refactoring, through building packages to adding new Git providers and developing new functionalities.

## Translations

Right now supported languages are English and Polish. Soon there will be possibility to translate project in Crowdin

## Roadmap ?

More like a wish list, as it depends on future needs of users and involvement of Open Source community:
- testing, testing, testing
- refactoring and review as this is initial work
- store credentials in more secure way
- Github adapter (right now only Gitlab is supported)
- utilising Markdown and WYSIWYM to create more rich text, which would still be easy to review by non-technical person

## Underlying technology

Python + PySimpleGUI + GitPython + Gitlab API packages.

## Code style

Blackd formatter and isort are your friends. Line-length 88. PRs are validated against them and finally by pycodestyle

# License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)