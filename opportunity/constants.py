class OpportunityStages:
    """Stage identifiers - edit these to change stage names throughout the system"""
    # Workflow stages (active progression)
    STAGE_1 = 'DISCOVERY'
    STAGE_2 = 'PROPOSAL'
    STAGE_3 = 'NEGOTIATION'
    
    # Terminal stages (end states)
    CLOSED_WON = 'CLOSED WON'
    CLOSED_LOST = 'CLOSED LOST'
    
    # Human-readable labels
    LABELS = {
        STAGE_1: 'Discovery',
        STAGE_2: 'Proposal',
        STAGE_3: 'Negotiation',
        CLOSED_WON: 'Closed Won',
        CLOSED_LOST: 'Closed Lost',
    }
    
    # For Django model choices (all possible stages)
    CHOICES = [
        (STAGE_1, LABELS[STAGE_1]),
        (STAGE_2, LABELS[STAGE_2]),
        (STAGE_3, LABELS[STAGE_3]),
        (CLOSED_WON, LABELS[CLOSED_WON]),
        (CLOSED_LOST, LABELS[CLOSED_LOST]),
    ]
    
    # Only workflow stages (for task management)
    WORKFLOW_STAGES = [STAGE_1, STAGE_2, STAGE_3]
    
    # All stages including terminal
    ALL = [STAGE_1, STAGE_2, STAGE_3, CLOSED_WON, CLOSED_LOST]
    
    # Stage progression mapping (only for workflow)
    NEXT_STAGE = {
        STAGE_1: STAGE_2,
        STAGE_2: STAGE_3,
        # Terminal stages have no next stage
    }
    
    # Completion timestamp field names (only for workflow)
    COMPLETION_FIELD = {
        STAGE_1: 'discovery_completed_at',
        STAGE_2: 'proposal_completed_at',
        # Terminal stages don't track completion
    }
