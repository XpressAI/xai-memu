import os
from memu import MemuClient
from xai_components.base import InArg, OutArg, Component, xai_component, secret
import time
import abc

@xai_component
class MemUAuthorize(Component):
    """A component to authorize and save the MemU client into the context."""

    base_url: InArg[str]
    api_key: InArg[secret]
    
    def execute(self, ctx) -> None:
        """Authorize the MemU client and save it into the context."""
        # Initialize MemU client

        base_url = "https://api.memu.so" if self.base_url.value is None else self.base_url.value
        
        if self.api_key.value is not None:
            memu_client = MemuClient(
                base_url=base_url, 
                api_key=self.api_key.value
            )
        else:
            memu_client = MemuClient(
                base_url=base_url, 
                api_key=os.getenv("MEMU_API_KEY")
            )
        
        # Save the client in the context
        ctx["memu_client"] = memu_client
        print("MemU client authorized and saved in context.")

@xai_component
class MemURememberConversation(Component):
    """A component to save and track conversation memories using MemU API."""
    
    conversation: InArg[list]
    user_id: InArg[str]
    user_name: InArg[str]
    agent_id: InArg[str]
    agent_name: InArg[str]
    status: OutArg[str]

    def execute(self, ctx) -> None:
        """Execute the memory saving process."""
        # Retrieve the MemU client from the context
        memu_client = ctx.get("memu_client")
        
        if not memu_client:
            print("Error: MemU client is not authorized. Please run MemUAuthorize first.")
            raise 'MemUAuthorize missing'

        convo = ""
        for turn in self.conversation.value:
            if isinstance(turn, str):
                convo += f"\n\n{turn}"
            else:
                convo += f"\n\n{turn['role']}: {turn['content']}"

        memo_response = memu_client.memorize_conversation(
            conversation=convo,
            user_id=self.user_id.value, 
            user_name=self.user_name.value, 
            agent_id=self.agent_id.value, 
            agent_name=self.agent_name.value
        )

        # Wait for completion
        while True:
            status = memu_client.get_task_status(memo_response.task_id)
            #print(f"Task status: {status.status}")
            if status.status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                self.status.value = status.status
                break
            time.sleep(2)

@xai_component
class MemURetrieveMemories(Component):
    """A component to retrieve memories related to a specific query using MemU API."""

    user_id: InArg[str]
    query: InArg[str]
    top_k: InArg[int]
    memories: OutArg[list]

    def execute(self, ctx) -> None:
        """Execute the memory retrieval process."""
        # Retrieve the MemU client from the context
        memu_client = ctx.get("memu_client")
        
        if not memu_client:
            print("Error: MemU client is not authorized. Please run MemUAuthorize first.")
            return

        # Retrieve memories
        memories = memu_client.retrieve_related_memory_items(
            user_id=self.user_id.value,
            query=self.query.value,
            top_k=self.top_k.value
        )
        
        print(memories)

        self.memories.value = memories.related_memories


@xai_component
class MemUAgentMemory(Component):
    """Creates a memory interface for the agent to store and query information using MemU API.

    ##### outPorts:
    - memory: The Memory to set on AgentInit
    """

    user_id: InArg[str]
    memory: OutArg['Memory']  # Specify that this will be a Memory type

    def execute(self, ctx) -> None:
        """Initialize the MemU client and set it as the memory for the agent."""
        memu_client = ctx.get("memu_client")
        
        if not memu_client:
            print("Error: MemU client is not authorized. Please run MemUAuthorize first.")
            return
        
        self.memory.value = MemUClientMemory(memu_client, user_id)


class Memory(abc.ABC):
    def query(self, query: str, n: int) -> list:
        pass

    def add(self, id: str, text: str, metadata: dict) -> None:
        pass

class MemUClientMemory(Memory):
    """Memory implementation using the MemU client."""

    user_id: str
    
    def __init__(self, memu_client: MemuClient, user_id: str):
        self.memu_client = memu_client
        self.user_id = user_id

    def query(self, query: str, top_k: int) -> list:
        """Query memories related to a specific query."""
        memories = self.memu_client.retrieve_related_memory_items(
            user_id=self.user_id,
            query=query,
            top_k=top_k
        )
        return memories.related_memories

    def add(self, id: str, text: str, metadata: dict) -> None:
        """Add a memory to the MemU."""
        self.memu_client.memorize_conversation(
            conversation=text,
            user_id=self.user_id,
            user_name=metadata.get("user_name", ""),
            agent_id=metadata.get("agent_id", "default_agent_id"),
            agent_name=metadata.get("agent_name", "Default Agent")
        )
