"""
Base class para plugins do Pluribus.

Plugins podem modificar comportamento da simulacao e adicionar metricas.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Set


class Plugin(ABC):
    """
    Interface base para plugins.

    Cada plugin pode:
    - Modificar agentes/estado a cada tick
    - Coletar metricas proprias
    - Formatar output proprio

    Atributos de classe:
    - priority: Ordem de execucao (menor = primeiro). Default 100.
    - dependencies: Set de nomes de plugins que devem executar antes.
    - conflicts: Set de nomes de plugins incompativeis.
    """

    # Prioridades sugeridas:
    # 0-20: Ambiente (Disaster, Season, Pollution)
    # 20-40: Economia (Tax, Market, Investment)
    # 40-60: Social (Trust, Gossip, Alliance, Teaching)
    # 60-80: Comportamento (Mood, Fatigue, Risk, MemoryDecay)
    # 80-100: Evolucao (Genetic, Speciation, Adaptation)
    # 100+: Pos-processamento (Death, Language, Censorship)

    priority: int = 100
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    @abstractmethod
    def get_name(self) -> str:
        """Nome do plugin para display"""
        pass

    def get_description(self) -> str:
        """Descricao curta do plugin"""
        return ""

    def get_params(self) -> Dict[str, Any]:
        """Retorna parametros configuraveis do plugin"""
        return {}

    def on_simulation_start(self, runner) -> None:
        """Chamado antes do primeiro tick"""
        pass

    def on_tick_start(self, runner, tick: int) -> None:
        """Chamado antes de cada tick"""
        pass

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        """Chamado depois de cada tick"""
        pass

    def on_simulation_end(self, runner) -> None:
        """Chamado quando simulacao termina"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna metricas especificas do plugin.

        Returns:
            Dict com metricas para exibir no resultado final
        """
        pass

    def format_stats(self) -> str:
        """
        Formata as stats para display.

        Returns:
            String formatada para printar
        """
        stats = self.get_stats()
        if not stats:
            return ""

        lines = [f"\n  [{self.get_name()}]", "  " + "-" * 20]
        for key, value in stats.items():
            if isinstance(value, float):
                lines.append(f"  {key}: {value:.1f}")
            else:
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)
