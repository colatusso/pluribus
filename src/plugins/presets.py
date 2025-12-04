"""
Presets de configuracao de plugins para cenarios interessantes.

Cada preset define uma combinacao de plugins com parametros ajustados
para criar dinamicas especificas e visiveis.
"""

PRESETS = {
    "survival": {
        "name": "Survival Mode",
        "description": "Selecao brutal. Agentes fracos morrem rapido, so os melhores sobrevivem.",
        "icon": "💀",
        "plugins": {
            "death": {},
            "disaster": {
                "probability": 0.15,
                "kill_chance": 0.25,
                "balance_damage": 0.4,
                "reset_factor": 0.5
            },
            "fatigue": {
                "fatigue_rate": 0.15,
                "recovery_rate": 0.1,
                "rest_threshold": 0.6,
                "performance_penalty": 0.5
            },
            "mood": {
                "initial_mood": 0.6,
                "success_boost": 0.05,
                "failure_penalty": 0.1,
                "mood_decay": 0.02,
                "chaos_threshold": 0.4
            },
            "genetic": {
                "reproduction_threshold": 0.85,
                "inheritance_factor": 0.9,
                "mutation_rate": 0.15,
                "mutation_strength": 0.25
            },
            "memory_decay": {
                "decay_rate": 0.05,
                "reinforce_threshold": 0.9
            }
        },
        "config_overrides": {
            "initial_balance": 150.0,
            "cost_per_attempt": 3.0
        }
    },

    "chaos": {
        "name": "Chaos World",
        "description": "Mundo hostil com desastres, mentiras e poluicao. Sobreviva ao caos.",
        "icon": "🌪️",
        "plugins": {
            "disaster": {
                "probability": 0.2,
                "kill_chance": 0.2,
                "balance_damage": 0.5,
                "reset_factor": 0.6
            },
            "gossip": {
                "lie_probability": 0.3,
                "lie_damage": 0.5,
                "detection_chance": 0.2
            },
            "pollution": {
                "pollution_rate": 0.1,
                "decay_rate": 0.001,
                "max_pollution": 0.8
            },
            "season": {
                "cycle_length": 50,
                "cost_amplitude": 0.8,
                "learning_amplitude": 0.6
            },
            "trust": {
                "initial_trust": 0.3,
                "trust_gain": 0.05,
                "trust_decay": 0.05,
                "trust_weight": 0.6
            },
            "risk": {
                "risk_variance": 0.5,
                "adaptive_risk": True
            },
            "death": {}
        },
        "config_overrides": {
            "initial_balance": 200.0,
            "cost_per_attempt": 2.0
        }
    },

    "utopia": {
        "name": "Utopia",
        "description": "Sociedade cooperativa com educacao, impostos justos e confianca alta.",
        "icon": "🌈",
        "plugins": {
            "tax": {
                "tax_rate": 0.3,
                "threshold_multiplier": 1.2,
                "redistribution": "proportional"
            },
            "teaching": {
                "teaching_cost": 2.0,
                "learning_boost": 0.6,
                "skill_threshold": 0.5
            },
            "trust": {
                "initial_trust": 0.8,
                "trust_gain": 0.2,
                "trust_decay": 0.01,
                "trust_weight": 0.8
            },
            "market": {
                "base_price": 5.0,
                "price_volatility": 0.05,
                "info_quality": 0.95
            },
            "alliance": {
                "num_alliances": 1,
                "loyalty_bonus": 1.0,
                "betrayal_chance": 0.0,
                "betrayal_reward": 0.0
            },
            "genetic": {
                "reproduction_threshold": 0.5,
                "inheritance_factor": 0.8,
                "mutation_rate": 0.1,
                "mutation_strength": 0.15
            },
            "memory_decay": {
                "decay_rate": 0.005,
                "reinforce_threshold": 0.7
            }
        },
        "config_overrides": {
            "initial_balance": 500.0,
            "cost_per_attempt": 1.0
        }
    },

    "corporate": {
        "name": "Corporate Jungle",
        "description": "Capitalismo extremo. Mercado feroz, ricos dominam, traicao e competicao.",
        "icon": "💼",
        "plugins": {
            "market": {
                "base_price": 20.0,
                "price_volatility": 0.4,
                "info_quality": 0.6
            },
            "investment": {
                "interest_rate": 0.1,
                "min_investment": 20.0,
                "investment_ratio": 0.5
            },
            "tax": {
                "tax_rate": 0.05,
                "threshold_multiplier": 2.0,
                "redistribution": "equal"
            },
            "alliance": {
                "num_alliances": 5,
                "loyalty_bonus": 0.2,
                "betrayal_chance": 0.15,
                "betrayal_reward": 200.0
            },
            "gossip": {
                "lie_probability": 0.25,
                "lie_damage": 0.3,
                "detection_chance": 0.25
            },
            "pollution": {
                "pollution_rate": 0.05,
                "decay_rate": 0.002,
                "max_pollution": 0.9
            },
            "risk": {
                "risk_variance": 0.4,
                "adaptive_risk": True
            },
            "adaptation": {
                "adaptation_rate": 0.2,
                "desperation_threshold": 5,
                "max_adaptation": 3.0
            },
            "death": {}
        },
        "config_overrides": {
            "initial_balance": 300.0,
            "cost_per_attempt": 2.0
        }
    },

    "evolution": {
        "name": "Evolutionary Arms Race",
        "description": "Especiacao e competicao. Evolucao acelerada com mutacao frequente.",
        "icon": "🧬",
        "plugins": {
            "genetic": {
                "reproduction_threshold": 0.6,
                "inheritance_factor": 0.85,
                "mutation_rate": 0.3,
                "mutation_strength": 0.3
            },
            "speciation": {
                "num_species": 4,
                "divergence_rate": 0.3,
                "competition_factor": 5.0
            },
            "adaptation": {
                "adaptation_rate": 0.15,
                "desperation_threshold": 7,
                "max_adaptation": 3.0
            },
            "risk": {
                "risk_variance": 0.35,
                "adaptive_risk": True
            },
            "disaster": {
                "probability": 0.1,
                "kill_chance": 0.15,
                "balance_damage": 0.3,
                "reset_factor": 0.4
            },
            "season": {
                "cycle_length": 60,
                "cost_amplitude": 0.5,
                "learning_amplitude": 0.4
            },
            "memory_decay": {
                "decay_rate": 0.03,
                "reinforce_threshold": 0.75
            },
            "mood": {
                "initial_mood": 0.7,
                "success_boost": 0.15,
                "failure_penalty": 0.1,
                "mood_decay": 0.01,
                "chaos_threshold": 0.35
            },
            "death": {}
        },
        "config_overrides": {
            "initial_balance": 250.0,
            "cost_per_attempt": 2.0
        }
    },

    "information": {
        "name": "Information Empire",
        "description": "Foco em linguagem, conhecimento e controle de informacao.",
        "icon": "📡",
        "plugins": {
            "language": {
                "compression_rate": 0.05,
                "max_compression": 0.8,
                "learning_curve": 0.3
            },
            "censorship": {
                "censor_ratio": 0.2,
                "block_probability": 0.5,
                "accuracy": 0.7
            },
            "trust": {
                "initial_trust": 0.5,
                "trust_gain": 0.15,
                "trust_decay": 0.02,
                "trust_weight": 0.7
            },
            "teaching": {
                "teaching_cost": 3.0,
                "learning_boost": 0.5,
                "skill_threshold": 0.6
            },
            "market": {
                "base_price": 8.0,
                "price_volatility": 0.15,
                "info_quality": 0.85
            },
            "gossip": {
                "lie_probability": 0.15,
                "lie_damage": 0.25,
                "detection_chance": 0.4
            },
            "tax": {
                "tax_rate": 0.15,
                "threshold_multiplier": 1.4,
                "redistribution": "equal"
            }
        },
        "config_overrides": {
            "initial_balance": 400.0,
            "cost_per_attempt": 1.5
        }
    }
}


def get_preset(name: str) -> dict:
    """Retorna preset por nome"""
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Preset '{name}' nao encontrado. Disponiveis: {available}")
    return PRESETS[name]


def list_presets() -> list:
    """Lista todos os presets disponiveis"""
    return [
        {
            "key": key,
            "name": preset["name"],
            "description": preset["description"],
            "icon": preset["icon"],
            "num_plugins": len(preset["plugins"])
        }
        for key, preset in PRESETS.items()
    ]
