# YNAB MCP

## About 

YNAB MCP is a Model Context Protocol (MCP) server that provides AI assistants access to the YNAB API. 

## Screenshots

![Create Transaction](images/transaction.png)
![Account Balance](images/account.png)
![Delete Transaction](images/delete-transaction.png)

## Supported Operations

#### General

- Read Budget & User info

#### Transactions

- Create
- Read
- Update
- Delete

#### Categories

- Read
- Update (Targets & Budgeted)

#### Payees

- Read

#### Accounts

- Read

## Installation Instructions

### Prerequisites

- Python 3.13
    - Tested on 3.13 but will probably work on previous versions
- YNAB Personal Access Token

### Setup

#### 1. Configure YNAB API Token

You need to obtain a Personal Access Token from YNAB:
1. Go to [YNAB Developer Settings](https://app.ynab.com/settings/developer)
2. Click "New Token"
3. Copy your Personal Access Token to the environment variable 'YNAB_API_TOKEN'

#### 2. Clone the Repository

```bash
git clone https://github.com/josephwalden13/YNAB-MCP.git
cd YNAB-MCP
```

#### 3. Build

```bash
docker compose up -d
```

### Claud Setup

These instructions are for the Anthropic Claud Desktop application. This should work with other MCP clients too.

#### 1. Open the MCP config

##### Windows

```bash
code $env:AppData\Claude\claude_desktop_config.json
```

##### Linux / MacOS

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### 2. Add entry for YNAB

```json
{
  "mcpServers": {
    "ynab": {
      "command": "docker",
      "args": [
        "attach",
        "ynab"
      ]
    }
  }
}
```