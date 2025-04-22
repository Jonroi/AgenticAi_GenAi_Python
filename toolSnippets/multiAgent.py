@register_tool()
def call_agent(action_context: ActionContext, 
               agent_name: str, 
               task: str) -> dict:
    """
    Invoke another agent to perform a specific task.
    
    Args:
        action_context: Contains registry of available agents
        agent_name: Name of the agent to call
        task: The task to ask the agent to perform
        
    Returns:
        The result from the invoked agent's final memory
    """
    # Get the agent registry from our context
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        raise ValueError("No agent registry found in context")
    
    # Get the agent's run function from the registry
    agent_run = agent_registry.get_agent(agent_name)
    if not agent_run:
        raise ValueError(f"Agent '{agent_name}' not found in registry")
    
    # Create a new memory instance for the invoked agent
    invoked_memory = Memory()
    
    try:
        # Run the agent with the provided task
        result_memory = agent_run(
            user_input=task,
            memory=invoked_memory,
            # Pass through any needed context properties
            action_context_props={
                'auth_token': action_context.get('auth_token'),
                'user_config': action_context.get('user_config'),
                # Don't pass agent_registry to prevent infinite recursion
            }
        )
        
        # Get the last memory item as the result
        if result_memory.items:
            last_memory = result_memory.items[-1]
            return {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "No result content")
            }
        else:
            return {
                "success": False,
                "error": "Agent failed to run."
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }