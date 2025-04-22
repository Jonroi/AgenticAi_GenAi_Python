@register_tool()
def call_agent(action_context: ActionContext, 
               agent_name: str, 
               task: str) -> dict:
    """
    Kutsu toista agenttia suorittamaan tietty tehtävä.
    
    Parametrit:
        action_context: Sisältää rekisterin käytettävissä olevista agenteista
        agent_name: Kutsuttavan agentin nimi
        task: Tehtävä, joka pyydetään agenttia suorittamaan
        
    Palauttaa:
        Tuloksen kutsutun agentin lopullisesta muistista
    """
    # Hanki agenttirekisteri kontekstista
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        raise ValueError("Kontekstista ei löydy agenttirekisteriä")
    
    # Hanki agentin suoritusfunktio rekisteristä
    agent_run = agent_registry.get_agent(agent_name)
    if not agent_run:
        raise ValueError(f"Agenttia '{agent_name}' ei löytynyt rekisteristä")
    
    # Luo uusi muistinstance kutsutulle agentille
    invoked_memory = Memory()
    
    try:
        # Suorita agentti annetulla tehtävällä
        result_memory = agent_run(
            user_input=task,
            memory=invoked_memory,
            # Välitä tarvittavat kontekstin ominaisuudet
            action_context_props={
                'auth_token': action_context.get('auth_token'),
                'user_config': action_context.get('user_config'),
                # Älä välitä agent_registryä rekursion estämiseksi
            }
        )
        
        # Hanki viimeisin muistielementti tulokseksi
        if result_memory.items:
            last_memory = result_memory.items[-1]
            return {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "Ei tulossisältöä")
            }
        else:
            return {
                "success": False,
                "error": "Agentin suoritus epäonnistui."
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }