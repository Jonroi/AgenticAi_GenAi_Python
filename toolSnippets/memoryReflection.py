@register_tool()
def call_agent_with_reflection(action_context: ActionContext, 
                             agent_name: str, 
                             task: str) -> dict:
    """Kutsu agenttia ja vastaanota heidän koko ajatusprosessinsa."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Luo uusi muistinstance kutsutulle agentille
    invoked_memory = Memory()
    
    # Suorita agentti
    result_memory = agent_run(
        user_input=task,
        memory=invoked_memory
    )
    
    # Hanki kutsujan muisti
    caller_memory = action_context.get_memory()
    
    # Lisää kaikki muistot kutsutulta agentilta kutsujan muistiin
    # vaikka voisimme jättää viimeisen muistin pois välttääksemme toistoa
    for memory_item in result_memory.items:
        caller_memory.add_memory({
            "type": f"{agent_name}_thought",  # Merkitse muistin lähde
            "content": memory_item["content"]
        })
    
    return {
        "result": result_memory.items[-1].get("content", "Ei tulosta"),
        "memories_added": len(result_memory.items)
    }