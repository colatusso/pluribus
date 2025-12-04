from .base import Plugin
from .death import DeathPlugin

# Environment plugins
from .environment import (
    DisasterPlugin,
    SeasonPlugin,
    MigrationPlugin,
    PollutionPlugin
)

# Economy plugins
from .economy import (
    MarketPlugin,
    TaxPlugin,
    InvestmentPlugin
)

# Social plugins
from .social import (
    TrustPlugin,
    GossipPlugin,
    AlliancePlugin,
    TeachingPlugin
)

# Behavior plugins
from .behavior import (
    MoodPlugin,
    FatiguePlugin,
    RiskPlugin,
    MemoryDecayPlugin
)

# Evolution plugins
from .evolution import (
    GeneticPlugin,
    SpeciationPlugin,
    AdaptationPlugin
)

# Communication plugins
from .communication import (
    LanguagePlugin,
    CensorshipPlugin
)

__all__ = [
    # Base
    "Plugin",
    "DeathPlugin",

    # Environment
    "DisasterPlugin",
    "SeasonPlugin",
    "MigrationPlugin",
    "PollutionPlugin",

    # Economy
    "MarketPlugin",
    "TaxPlugin",
    "InvestmentPlugin",

    # Social
    "TrustPlugin",
    "GossipPlugin",
    "AlliancePlugin",
    "TeachingPlugin",

    # Behavior
    "MoodPlugin",
    "FatiguePlugin",
    "RiskPlugin",
    "MemoryDecayPlugin",

    # Evolution
    "GeneticPlugin",
    "SpeciationPlugin",
    "AdaptationPlugin",

    # Communication
    "LanguagePlugin",
    "CensorshipPlugin",
]

# Plugin registry for easy access
PLUGIN_REGISTRY = {
    # Environment
    "disaster": DisasterPlugin,
    "season": SeasonPlugin,
    "migration": MigrationPlugin,
    "pollution": PollutionPlugin,

    # Economy
    "market": MarketPlugin,
    "tax": TaxPlugin,
    "investment": InvestmentPlugin,

    # Social
    "trust": TrustPlugin,
    "gossip": GossipPlugin,
    "alliance": AlliancePlugin,
    "teaching": TeachingPlugin,

    # Behavior
    "mood": MoodPlugin,
    "fatigue": FatiguePlugin,
    "risk": RiskPlugin,
    "memory_decay": MemoryDecayPlugin,

    # Evolution
    "genetic": GeneticPlugin,
    "speciation": SpeciationPlugin,
    "adaptation": AdaptationPlugin,

    # Communication
    "language": LanguagePlugin,
    "censorship": CensorshipPlugin,

    # Core
    "death": DeathPlugin,
}


def get_plugin(name: str, **kwargs) -> Plugin:
    """
    Factory function para criar plugins por nome.

    Args:
        name: Nome do plugin (lowercase)
        **kwargs: Parametros do plugin

    Returns:
        Instancia do plugin

    Raises:
        ValueError: Se plugin nao existe
    """
    if name not in PLUGIN_REGISTRY:
        available = ", ".join(PLUGIN_REGISTRY.keys())
        raise ValueError(f"Plugin '{name}' nao encontrado. Disponiveis: {available}")

    return PLUGIN_REGISTRY[name](**kwargs)
