# MemU Component Library

This repository contains a set of components designed to integrate with the MemU API, allowing agents to store, retrieve, and manage conversational memories. The components are built using the Xircuits framework.

## Components Overview

### 1. MemUAuthorize
A component to authorize and save the MemU client into the context.

#### Inputs:
- `base_url` (str): The base URL for the MemU API.
- `api_key` (secret): The API key for authenticating with MemU.

#### Outputs:
- None.  Saves the client to the context as `memu_client`


### 2. MemURememberConversation

A component to save and track conversation memories using the MemU API.

#### Inputs:

- conversation (list): The conversation to save
- user_id (str): The user's unique identifier.
- user_name (str): The user's name.
- agent_id (str): The agent's unique identifier.
- agent_name (str): The agent's name.

##### Outputs:

- None

### 3. MemURetrieveMemories

A component to retrieve memories related to a specific query using the MemU API.

#### Inputs:

- user_id (str): The user's unique identifier.
- query (str): The query to search memories.
- top_k (int): The number of top memories to retrieve.

#### Outputs:

- memories (list): A list of related memories.


### 4. MemUAgentMemory

Creates a memory interface for an agent (using the xai-agent component library) to store and query information using the MemU API instead of locally with Numpy or with Vecto.

#### Inputs:
- user_id (str): The user's unique identifier.

#### Outputs:

- memory (Memory): The memory interface for the agent.


### Installation
To use this library, ensure you have the required dependencies installed. You can install them using pip:

```bash

xircuits install https://github.com/XpressAI/xai-memu

```

