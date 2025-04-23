@register_tool(description="Delegate a task to another agent with selected context")
def call_agent_with_selected_context(action_context: ActionContext,
                                   agent_name: str,
                                   task: str) -> dict:
    """Kutsuu agenttia LLM:n valitsemilla relevantilla muistoilla."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Hanki nykyiset muistot ja lisää tunnisteet
    current_memory = action_context.get_memory()
    memory_with_ids = []
    for idx, item in enumerate(current_memory.items):
        memory_with_ids.append({
            **item,
            "memory_id": f"mem_{idx}"
        })
    
    # Luo skeema muistojen valintaa varten
    selection_schema = {
        "type": "object",
        "properties": {
            "selected_memories": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "Muiston tunniste, joka sisällytetään"
                }
            },
            "reasoning": {
                "type": "string",
                "description": "Selitys, miksi nämä muistot valittiin"
            }
        },
        "required": ["selected_memories", "reasoning"]
    }
    
    # Muotoile muistot LLM:n tarkastelua varten
    memory_text = "\n".join([
        f"Muisto {m['memory_id']}: {m['content']}" 
        for m in memory_with_ids
    ])
    
    # Pyydä LLM:ää valitsemaan relevantit muistot
    selection_prompt = f"""Tarkastele näitä muistoja ja valitse ne, jotka ovat oleellisia tätä tehtävää varten:

Tehtävä: {task}

Saatavilla olevat muistot:
{memory_text}

Valitse muistot, jotka tarjoavat tärkeää kontekstia tai tietoa tähän tiettyyn tehtävään.
Selitä valintaprosessisi."""

    # Itseohjautuva logiikka tärkeimpien muistojen löytämiseksi
    selection = prompt_llm_for_json(
        action_context=action_context,
        schema=selection_schema,
        prompt=selection_prompt
    )
    
    # Luo suodatetut muistot valinnan perusteella
    filtered_memory = Memory()
    selected_ids = set(selection["selected_memories"])
    for item in memory_with_ids:
        if item["memory_id"] in selected_ids:
            # Poista väliaikainen memory_id ennen lisäämistä
            item_copy = item.copy()
            del item_copy["memory_id"]
            filtered_memory.add_memory(item_copy)
    
    # Suorita agentti valituilla muistoilla
    result_memory = agent_run(
        user_input=task,
        memory=filtered_memory
    )
    
    # Lisää tulokset ja valinnan perustelut alkuperäisiin muistoihin
    current_memory.add_memory({
        "type": "system",
        "content": f"Muistojen valinnan perustelut: {selection['reasoning']}"
    })
    
    for memory_item in result_memory.items:
        current_memory.add_memory(memory_item)
    
    return {
        "result": result_memory.items[-1].get("content", "Ei tulosta"),
        "shared_memories": len(filtered_memory.items),
        "selection_reasoning": selection["reasoning"]
    }


###############################

# Example memory contents:
memories = [
    {"type": "user", "content": "We need to build a new reporting dashboard"},
    {"type": "assistant", "content": "Initial cost estimate: $50,000"},
    {"type": "user", "content": "That seems high"},
    {"type": "assistant", "content": "Breakdown: $20k development, $15k design..."},
    {"type": "system", "content": "Project deadline updated to Q3"},
    {"type": "user", "content": "Can we reduce the cost?"}
]

# LLM's selection might return:
{
    "selected_memories": ["mem_1", "mem_3", "mem_5"],
    "reasoning": "Selected memories containing cost information and the request for cost reduction, excluding project timeline and general discussion as they're not directly relevant to the budget review task."
}