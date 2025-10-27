# Stacked PR Manager (work in progress)

A CLI tool for managing stacked (dependent) Pull Requests on GitHub. If you've ever worked with a chain of PRs where each one depends on the previous, you know how time-consuming it is to merge them all - especially when you need to wait for CI/CD pipelines to finish after each one. This tool automates the tedious parts, so you go make coffee in the meantime.

## The Problem

You're working on a big feature split into multiple PRs (here only 3, but you can have way more):
- PR #1: `main` <- `feature-part1`
- PR #2: `feature-part1` <- `feature-part2`
- PR #3: `feature-part2` <- `feature-part3`

Now someone requests changes to PR #1. You update it, merge it into `feature-part2`, then merge `feature-part2` into `feature-part3`. Then you push all three branches. Repeat for every change...

Yeah, this tool automates that.

## Features

- **Create stacked PRs** from a simple text file listing your branches
- **Push entire chains** at once
- **Merge base branches into heads** automatically (propagate changes up the stack)
- **Rename PRs** in bulk with templates
- **Request reviews** for all PRs in a chain

## Setup

### Requirements
- Python 3.10+
- Poetry
- GitHub access token

### Installation

```bash
git clone https://github.com/karolzlot/stacked-pr-manager.git
cd stacked-pr-manager
poetry install
```

### Configuration

Create a `.env` file in the project root:

```bash
GITHUB_ACCESS_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_username
GITHUB_REPO=owner/repo-name
LOCAL_REPO_PATH=/path/to/your/local/repo
REVIEWERS=reviewer1,reviewer2
BRANCH_PREFIX=feature/
```

## Usage

Currently no CLI, the tool works by running individual Python modules. Here are the main commands:

...

TODO: finish this part of documentation
