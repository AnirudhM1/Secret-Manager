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
```bash
# coming soon!
```

