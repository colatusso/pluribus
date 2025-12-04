"""
Plugins de comportamento para Pluribus.

Implementam estados psicologicos que afetam performance.
"""
import random
import numpy as np
from typing import Dict, Any, List, Set
from .base import Plugin


class MoodPlugin(Plugin):
    """
    Sistema de humor/moral.

    Moral afeta qualidade do aprendizado:
    - Moral alta: learning rate normal, exploracao inteligente
    - Moral baixa: learning rate reduzido, exploracao caotica

    Sucesso aumenta moral, fracasso diminui.
    """

    priority = 65
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        initial_mood: float = 0.7,
        success_boost: float = 0.1,
        failure_penalty: float = 0.05,
        mood_decay: float = 0.01,
        chaos_threshold: float = 0.3
    ):
        """
        Args:
            initial_mood: Moral inicial (0-1)
            success_boost: Aumento por melhora
            failure_penalty: Reducao por fracasso
            mood_decay: Decay natural por tick
            chaos_threshold: Abaixo disso, exploracao fica caotica
        """
        self.initial_mood = initial_mood
        self.success_boost = success_boost
        self.failure_penalty = failure_penalty
        self.mood_decay = mood_decay
        self.chaos_threshold = chaos_threshold

        # Mood por agente
        self.moods: Dict[int, float] = {}
        # Learning rates originais
        self._original_lr: Dict[int, float] = {}

    def get_name(self) -> str:
        return "Mood"

    def get_description(self) -> str:
        return "Moral afeta aprendizado e exploracao"

    def get_params(self) -> Dict[str, Any]:
        return {
            "initial_mood": self.initial_mood,
            "success_boost": self.success_boost,
            "failure_penalty": self.failure_penalty,
            "mood_decay": self.mood_decay,
            "chaos_threshold": self.chaos_threshold
        }

    def on_simulation_start(self, runner) -> None:
        self.moods = {a.node_id: self.initial_mood for a in runner.agents}

        # Guarda learning rates originais
        for agent in runner.agents:
            if hasattr(agent.strategy, 'learning_rate'):
                self._original_lr[agent.node_id] = agent.strategy.learning_rate

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents:
            return

        for i, agent in enumerate(runner.agents):
            if i >= len(tick_rewards):
                continue

            reward = tick_rewards[i]
            agent_id = agent.node_id

            # Inicializa mood se agente novo (criado por GeneticPlugin etc)
            if agent_id not in self.moods:
                self.moods[agent_id] = self.initial_mood
                if hasattr(agent.strategy, 'learning_rate'):
                    self._original_lr[agent_id] = agent.strategy.learning_rate

            # Atualiza mood baseado em performance
            if reward > agent.best_reward:
                # Melhorou - aumenta moral
                self.moods[agent_id] = min(1.0, self.moods[agent_id] + self.success_boost)
            else:
                # Nao melhorou - diminui moral
                self.moods[agent_id] = max(0.1, self.moods[agent_id] - self.failure_penalty)

            # Decay natural
            self.moods[agent_id] *= (1 - self.mood_decay)

            # Aplica efeitos do mood
            self._apply_mood_effects(agent)

    def _apply_mood_effects(self, agent) -> None:
        """Aplica efeitos do mood no agente"""
        mood = self.moods.get(agent.node_id, 0.5)

        # Ajusta learning rate usando modifier system
        if hasattr(agent.strategy, 'learning_rate'):
            # Registra multiplicador pro modifier system
            base_lr = self._original_lr.get(agent.node_id, agent.strategy.learning_rate)
            modifier = agent.modifiers.get_modifier('learning_rate', base_lr)
            modifier.set_multiplier('mood', mood)

        # Mood muito baixo = exploracao caotica
        if mood < self.chaos_threshold:
            # Adiciona ruido aleatorio na policy
            noise = np.random.uniform(0, 0.1, agent.P.shape)
            agent.P = agent.P + noise

            # Renormaliza
            row_sums = agent.P.sum(axis=1, keepdims=True)
            agent.P = agent.P / row_sums

    def get_stats(self) -> Dict[str, Any]:
        if not self.moods:
            return {}

        moods = list(self.moods.values())
        depressed = sum(1 for m in moods if m < self.chaos_threshold)

        return {
            "Moral media": f"{np.mean(moods):.2f}",
            "Moral min": f"{min(moods):.2f}",
            "Moral max": f"{max(moods):.2f}",
            "Deprimidos": depressed
        }


class FatiguePlugin(Plugin):
    """
    Sistema de fadiga.

    Muitas tentativas seguidas causam cansaco.
    Agentes cansados tem performance reduzida.
    Podem "descansar" pulando tick para recuperar.
    """

    priority = 68
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        fatigue_rate: float = 0.05,
        recovery_rate: float = 0.2,
        rest_threshold: float = 0.8,
        performance_penalty: float = 0.3
    ):
        """
        Args:
            fatigue_rate: Aumento de fadiga por tick
            recovery_rate: Recuperacao por tick de descanso
            rest_threshold: Fadiga acima disso forca descanso
            performance_penalty: Penalidade no learning quando cansado
        """
        self.fatigue_rate = fatigue_rate
        self.recovery_rate = recovery_rate
        self.rest_threshold = rest_threshold
        self.performance_penalty = performance_penalty

        # Fadiga por agente (0 = descansado, 1 = exausto)
        self.fatigue: Dict[int, float] = {}
        self.rest_ticks = 0

    def get_name(self) -> str:
        return "Fatigue"

    def get_description(self) -> str:
        return "Cansaco reduz performance, descanso recupera"

    def get_params(self) -> Dict[str, Any]:
        return {
            "fatigue_rate": self.fatigue_rate,
            "recovery_rate": self.recovery_rate,
            "rest_threshold": self.rest_threshold,
            "performance_penalty": self.performance_penalty
        }

    def on_simulation_start(self, runner) -> None:
        self.fatigue = {a.node_id: 0.0 for a in runner.agents}
        self.rest_ticks = 0

    def on_tick_start(self, runner, tick: int) -> None:
        # Agentes muito cansados descansam
        # Marca mas NAO remove (remover causa bugs)
        if not hasattr(runner, '_resting_agents'):
            runner._resting_agents = set()

        runner._resting_agents.clear()

        for agent in runner.agents:
            if self.fatigue.get(agent.node_id, 0) >= self.rest_threshold:
                runner._resting_agents.add(agent.node_id)
                # Recupera
                self.fatigue[agent.node_id] = max(
                    0,
                    self.fatigue[agent.node_id] - self.recovery_rate
                )
                self.rest_ticks += 1

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        # Aumenta fadiga dos que trabalharam (nao descansaram)
        resting_ids = getattr(runner, '_resting_agents', set())

        for agent in runner.agents:
            agent_id = agent.node_id

            # Inicializa se agente novo
            if agent_id not in self.fatigue:
                self.fatigue[agent_id] = 0.0

            # Agentes descansando nao aumentam fadiga
            if agent_id in resting_ids:
                continue

            # Aumenta fadiga dos que trabalharam
            self.fatigue[agent_id] = min(
                1.0,
                self.fatigue[agent_id] + self.fatigue_rate
            )

            # Aplica penalidade de performance usando modifier system
            fatigue_level = self.fatigue[agent_id]
            if fatigue_level > 0.5 and hasattr(agent.strategy, 'learning_rate'):
                # Reduz efetividade do aprendizado
                penalty_mult = 1.0 - (fatigue_level * self.performance_penalty)
                modifier = agent.modifiers.get_modifier('learning_rate', agent.strategy.learning_rate)
                modifier.set_multiplier('fatigue', penalty_mult)

    def get_stats(self) -> Dict[str, Any]:
        if not self.fatigue:
            return {}

        fatigues = list(self.fatigue.values())
        exhausted = sum(1 for f in fatigues if f >= self.rest_threshold)

        return {
            "Fadiga media": f"{np.mean(fatigues):.2f}",
            "Exaustos": exhausted,
            "Ticks descansando": self.rest_ticks
        }


class RiskPlugin(Plugin):
    """
    Perfis de aversao ao risco.

    Alguns agentes sao conservadores (exploram pouco),
    outros sao arriscados (exploram muito).

    Afeta estrategia de exploracao.
    """

    priority = 62
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        risk_variance: float = 0.3,
        adaptive_risk: bool = True
    ):
        """
        Args:
            risk_variance: Variancia nos perfis de risco
            adaptive_risk: Se True, risco muda baseado em sucesso
        """
        self.risk_variance = risk_variance
        self.adaptive_risk = adaptive_risk

        # Perfil de risco por agente (0 = conservador, 1 = arriscado)
        self.risk_profiles: Dict[int, float] = {}

    def get_name(self) -> str:
        return "Risk"

    def get_description(self) -> str:
        return "Perfis de aversao ao risco variam exploracao"

    def get_params(self) -> Dict[str, Any]:
        return {
            "risk_variance": self.risk_variance,
            "adaptive_risk": self.adaptive_risk
        }

    def on_simulation_start(self, runner) -> None:
        # Gera perfis aleatorios
        self.risk_profiles = {}
        for agent in runner.agents:
            # Distribuicao normal centrada em 0.5
            risk = np.clip(
                np.random.normal(0.5, self.risk_variance),
                0.1, 0.9
            )
            self.risk_profiles[agent.node_id] = risk

            # Aplica perfil na strategy
            self._apply_risk_profile(agent)

    def _apply_risk_profile(self, agent) -> None:
        """Aplica perfil de risco na strategy"""
        risk = self.risk_profiles.get(agent.node_id, 0.5)

        # Se strategy tem epsilon, ajusta
        if hasattr(agent.strategy, 'epsilon'):
            # Arriscado = mais epsilon
            agent.strategy.epsilon *= (0.5 + risk)

        # Arriscados tambem tem learning rate mais alto
        if hasattr(agent.strategy, 'learning_rate'):
            agent.strategy.learning_rate *= (0.8 + risk * 0.4)

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not self.adaptive_risk:
            return

        # Adapta risco baseado em sucesso
        for i, agent in enumerate(runner.agents):
            if i >= len(tick_rewards):
                continue

            reward = tick_rewards[i]
            agent_id = agent.node_id

            # Inicializa se agente novo
            if agent_id not in self.risk_profiles:
                risk = np.clip(np.random.normal(0.5, self.risk_variance), 0.1, 0.9)
                self.risk_profiles[agent_id] = risk
                self._apply_risk_profile(agent)

            # Sucesso = mais conservador (esta funcionando)
            # Fracasso = mais arriscado (precisa mudar)
            if reward > agent.best_reward:
                self.risk_profiles[agent_id] = max(
                    0.1,
                    self.risk_profiles[agent_id] * 0.95
                )
            else:
                self.risk_profiles[agent_id] = min(
                    0.9,
                    self.risk_profiles[agent_id] * 1.02
                )

    def get_stats(self) -> Dict[str, Any]:
        if not self.risk_profiles:
            return {}

        risks = list(self.risk_profiles.values())
        conservative = sum(1 for r in risks if r < 0.3)
        risky = sum(1 for r in risks if r > 0.7)

        return {
            "Risco medio": f"{np.mean(risks):.2f}",
            "Conservadores": conservative,
            "Arriscados": risky
        }


class MemoryDecayPlugin(Plugin):
    """
    Esquecimento - conhecimento antigo se perde.

    Policy decai em direcao a uniforme se nao for reforçada.
    Forca aprendizado continuo.
    """

    priority = 70
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        decay_rate: float = 0.02,
        reinforce_threshold: float = 0.8
    ):
        """
        Args:
            decay_rate: Quanto da policy esquece por tick
            reinforce_threshold: Reward acima disso reforça memoria
        """
        self.decay_rate = decay_rate
        self.reinforce_threshold = reinforce_threshold

        self.total_decay = 0.0

    def get_name(self) -> str:
        return "MemoryDecay"

    def get_description(self) -> str:
        return "Conhecimento antigo e esquecido gradualmente"

    def get_params(self) -> Dict[str, Any]:
        return {
            "decay_rate": self.decay_rate,
            "reinforce_threshold": self.reinforce_threshold
        }

    def on_simulation_start(self, runner) -> None:
        self.total_decay = 0.0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        for i, agent in enumerate(runner.agents):
            if i >= len(tick_rewards):
                continue

            reward = tick_rewards[i]

            # Se reward alto, reforça (nao esquece)
            if reward >= agent.best_reward * self.reinforce_threshold:
                continue

            # Decay em direcao a uniforme
            uniform = np.ones_like(agent.P) / agent.P.shape[1]
            decay = self.decay_rate * (1 - reward / 100.0)  # Mais decay se reward baixo

            old_P = agent.P.copy()
            agent.P = (1 - decay) * agent.P + decay * uniform

            # Mede quanto esqueceu
            self.total_decay += np.abs(agent.P - old_P).sum()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Decay total": f"{self.total_decay:.1f}"
        }
