# Secret Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

A simple python CLI to help me manage and track secrets across python projects

## Installation

You can install Secret Manager directly from GitHub:

```bash
pip install git+https://github.com/AnirudhM1/Secret-Manager.git
```

Or install from source:

```bash
git clone https://github.com/AnirudhM1/Secret-Manager.git
cd Secret-Manager
pip install .
```

## Usage

### Register a Project

Register the current directory as a project:

```bash
secrets register
```

### Track Environment Files

Track an environment file for a specific environment:

```bash
secrets track .env.local --environment local
secrets track .env.dev --environment dev
secrets track .env.prod --environment prod
```

If you don't specify an environment, you'll be prompted to select one.

### List Tracked Secrets

List all secrets tracked in the current project:

```bash
secrets list
```

### Compare Environments

Compare secrets between two environments:

```bash
# Compare local and dev environments (default)
secrets diff

# Compare specific environments
secrets diff dev prod
```

### Unregister a Project

Unregister the current project:

```bash
secrets unregister
```

### Remote AWS S3 Syncing

#### Managing Remotes

Add a new remote backend:

```bash
secrets remote add my-s3-remote
# Follow the prompts to setup a S3 remote
```

> [!NOTE]
> Currently only S3 backend is supported

List all configured remotes:

```bash
secrets remote list
```

Show details of a specific remote:

```bash
secrets remote show my-s3-remote
```

Remove a remote backend:

```bash
secrets remote remove my-s3-remote
```

#### Working with Remote Secrets

Configure remote tracking for an environment:

```bash
secrets set-remote prod
```

Push local secrets to the remote backend:

```bash
secrets push prod
# With confirmation bypass
secrets push prod --force
```

> [!WARNING]
> This overrides the remote file with the contents of the local file
> Make sure that the local file contains changes present in the remote to avoid discarding them

Fetch and display remote secrets without modifying local files:

```bash
secrets fetch prod
```

Pull secrets from remote and update local files:

```bash
secrets pull prod
# With confirmation bypass
secrets pull prod --force
```

> [!WARNING]
> This overrides the remote file with the contents of the local file

Remove remote association from a tracked secret:

```bash
secrets unset-remote prod
```

