"""
Plugins sociais para Pluribus.

Implementam dinamicas de confianca, fofoca, aliancas e ensino.
"""
import random
import numpy as np
from typing import Dict, Any, List, Set, Tuple
from .base import Plugin


class TrustPlugin(Plugin):
    """
    Sistema de reputacao baseado em confianca.

    Agentes ganham trust quando compartilham info util,
    perdem quando compartilham info ruim. Agentes preferem
    ouvir quem tem mais trust.

    Cria hierarquia social baseada em merito.
    """

    priority = 45
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        initial_trust: float = 0.5,
        trust_gain: float = 0.1,
        trust_decay: float = 0.02,
        trust_weight: float = 0.5
    ):
        """
        Args:
            initial_trust: Trust inicial de cada agente (0-1)
            trust_gain: Quanto ganha por ajuda bem sucedida
            trust_decay: Decay natural por tick
            trust_weight: Peso do trust na comunicacao
        """
        self.initial_trust = initial_trust
        self.trust_gain = trust_gain
        self.trust_decay = trust_decay
        self.trust_weight = trust_weight

        # Trust por agente
        self.trust_scores: Dict[int, float] = {}
        self.help_given: Dict[int, int] = {}

    def get_name(self) -> str:
        return "Trust"

    def get_description(self) -> str:
        return "Sistema de reputacao baseado em ajuda"

    def get_params(self) -> Dict[str, Any]:
        return {
            "initial_trust": self.initial_trust,
            "trust_gain": self.trust_gain,
            "trust_decay": self.trust_decay,
            "trust_weight": self.trust_weight
        }

    def on_simulation_start(self, runner) -> None:
        self.trust_scores = {a.node_id: self.initial_trust for a in runner.agents}
        self.help_given = {a.node_id: 0 for a in runner.agents}

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents:
            return

        # Decay natural
        for agent_id in self.trust_scores:
            self.trust_scores[agent_id] = max(
                0.1,
                self.trust_scores[agent_id] * (1 - self.trust_decay)
            )

        # Identifica quem melhorou (potencial ajudante)
        for i, agent in enumerate(runner.agents):
            if i >= len(tick_rewards):
                continue

            reward = tick_rewards[i]

            # Se melhorou significativamente, pode ter recebido boa info
            if reward > agent.best_reward * 0.8:
                # Credita vizinhos (quem pode ter ajudado)
                for neighbor_id in agent.neighbors:
                    if neighbor_id in self.trust_scores:
                        self.trust_scores[neighbor_id] = min(
                            1.0,
                            self.trust_scores[neighbor_id] + self.trust_gain
                        )
                        self.help_given[neighbor_id] = self.help_given.get(neighbor_id, 0) + 1

        # Modifica comunicacao baseada em trust
        self._apply_trust_to_communication(runner)

    def _apply_trust_to_communication(self, runner) -> None:
        """Modifica gamma de comunicacao baseado em trust"""
        for agent in runner.agents:
            # Vizinhos com mais trust tem mais influencia
            if hasattr(agent, 'neighbors') and agent.neighbors:
                avg_neighbor_trust = sum(
                    self.trust_scores.get(n, 0.5) for n in agent.neighbors
                ) / len(agent.neighbors)

                # Ajusta receptividade baseado em trust dos vizinhos
                # (isso sera usado pelo comm_mode)
                agent._trust_modifier = avg_neighbor_trust * self.trust_weight

    def get_stats(self) -> Dict[str, Any]:
        if not self.trust_scores:
            return {}

        scores = list(self.trust_scores.values())
        most_trusted = max(self.trust_scores.items(), key=lambda x: x[1])

        return {
            "Trust medio": f"{np.mean(scores):.2f}",
            "Trust max": f"{max(scores):.2f}",
            "Mais confiavel": f"Agente {most_trusted[0]}",
            "Total ajudas": sum(self.help_given.values())
        }


class GossipPlugin(Plugin):
    """
    Fofoca e desinformacao.

    Agentes podem mentir sobre seu progresso, espalhando
    informacao falsa que prejudica quem acredita.

    Simula propaganda e fake news.
    """

    priority = 50
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        lie_probability: float = 0.1,
        lie_damage: float = 0.2,
        detection_chance: float = 0.3
    ):
        """
        Args:
            lie_probability: Chance de um agente mentir
            lie_damage: Quanto a mentira prejudica quem acredita
            detection_chance: Chance de detectar mentira
        """
        self.lie_probability = lie_probability
        self.lie_damage = lie_damage
        self.detection_chance = detection_chance

        self.lies_told = 0
        self.lies_detected = 0
        self.victims = 0

    def get_name(self) -> str:
        return "Gossip"

    def get_description(self) -> str:
        return "Fofoca e desinformacao entre agentes"

    def get_params(self) -> Dict[str, Any]:
        return {
            "lie_probability": self.lie_probability,
            "lie_damage": self.lie_damage,
            "detection_chance": self.detection_chance
        }

    def on_simulation_start(self, runner) -> None:
        self.lies_told = 0
        self.lies_detected = 0
        self.victims = 0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if len(runner.agents) < 2:
            return

        for agent in runner.agents:
            if random.random() < self.lie_probability:
                self._spread_lie(agent, runner)

    def _spread_lie(self, liar, runner) -> None:
        """Espalha mentira para vizinhos"""
        self.lies_told += 1

        # Cria informacao falsa (policy com ruido)
        fake_policy = np.random.dirichlet(
            np.ones(liar.P.shape[1]),
            size=liar.P.shape[0]
        )

        # Espalha para vizinhos
        for neighbor_id in liar.neighbors:
            neighbor = next((a for a in runner.agents if a.node_id == neighbor_id), None)
            if not neighbor:
                continue

            # Chance de detectar
            if random.random() < self.detection_chance:
                self.lies_detected += 1
                continue

            # Vitima acredita na mentira
            self.victims += 1
            gamma = self.lie_damage
            neighbor.P = (1 - gamma) * neighbor.P + gamma * fake_policy

    def get_stats(self) -> Dict[str, Any]:
        detection_rate = (
            self.lies_detected / self.lies_told * 100
            if self.lies_told > 0 else 0
        )
        return {
            "Mentiras contadas": self.lies_told,
            "Mentiras detectadas": self.lies_detected,
            "Vitimas": self.victims,
            "Taxa deteccao": f"{detection_rate:.0f}%"
        }


class AlliancePlugin(Plugin):
    """
    Formacao de aliancas/faccoes.

    Agentes formam grupos e compartilham informacao apenas
    dentro do grupo. Traicao pode dar vantagem individual.

    Simula tribalismo e cooperacao seletiva.
    """

    priority = 42
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        num_alliances: int = 3,
        loyalty_bonus: float = 0.5,
        betrayal_chance: float = 0.05,
        betrayal_reward: float = 100.0
    ):
        """
        Args:
            num_alliances: Numero de aliancas
            loyalty_bonus: Bonus de gamma para aliados
            betrayal_chance: Chance de trair alianca
            betrayal_reward: Bonus de balance por traicao
        """
        self.num_alliances = num_alliances
        self.loyalty_bonus = loyalty_bonus
        self.betrayal_chance = betrayal_chance
        self.betrayal_reward = betrayal_reward

        # Alianca de cada agente
        self.alliances: Dict[int, int] = {}
        self.betrayals = 0

    def get_name(self) -> str:
        return "Alliance"

    def get_description(self) -> str:
        return "Formacao de grupos com lealdade e traicao"

    def get_params(self) -> Dict[str, Any]:
        return {
            "num_alliances": self.num_alliances,
            "loyalty_bonus": self.loyalty_bonus,
            "betrayal_chance": self.betrayal_chance,
            "betrayal_reward": self.betrayal_reward
        }

    def on_simulation_start(self, runner) -> None:
        # Distribui agentes em aliancas
        self.alliances = {}
        for i, agent in enumerate(runner.agents):
            self.alliances[agent.node_id] = i % self.num_alliances

        self.betrayals = 0

        # Atualiza vizinhos para priorizar aliados
        self._update_neighbors(runner)

    def _update_neighbors(self, runner) -> None:
        """Prioriza vizinhos da mesma alianca"""
        for agent in runner.agents:
            my_alliance = self.alliances.get(agent.node_id, 0)

            # Encontra aliados
            allies = [
                a.node_id for a in runner.agents
                if a.node_id != agent.node_id
                and self.alliances.get(a.node_id, -1) == my_alliance
            ]

            # Prioriza aliados nos vizinhos
            if allies:
                # Mantem alguns vizinhos originais, adiciona aliados
                num_allies = min(len(allies), len(agent.neighbors) // 2 + 1)
                ally_neighbors = random.sample(allies, num_allies)

                # Completa com vizinhos originais
                other_neighbors = [n for n in agent.neighbors if n not in ally_neighbors]
                agent.neighbors = ally_neighbors + other_neighbors[:len(agent.neighbors) - num_allies]

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents:
            return

        # Chance de traicao
        for agent in runner.agents:
            if random.random() < self.betrayal_chance:
                self._betray(agent, runner)

    def _betray(self, traitor, runner) -> None:
        """Agente trai alianca e muda de grupo"""
        old_alliance = self.alliances.get(traitor.node_id, 0)

        # Muda para outra alianca
        new_alliance = (old_alliance + 1) % self.num_alliances
        self.alliances[traitor.node_id] = new_alliance

        # Ganha recompensa
        traitor.balance += self.betrayal_reward
        self.betrayals += 1

        # Atualiza vizinhos
        self._update_neighbors(runner)

    def get_stats(self) -> Dict[str, Any]:
        # Conta membros por alianca
        alliance_counts = {}
        for alliance in self.alliances.values():
            alliance_counts[alliance] = alliance_counts.get(alliance, 0) + 1

        return {
            "Aliancas": self.num_alliances,
            "Traicoes": self.betrayals,
            "Distribuicao": str(alliance_counts)
        }


class TeachingPlugin(Plugin):
    """
    Sistema de mentoria.

    Agentes experientes (alto reward) ensinam novatos.
    Custo para professor, beneficio para aluno.

    Simula educacao e transferencia de conhecimento.
    """

    priority = 55
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        teaching_cost: float = 5.0,
        learning_boost: float = 0.4,
        skill_threshold: float = 0.7
    ):
        """
        Args:
            teaching_cost: Custo de balance para ensinar
            learning_boost: Quanto o aluno absorve (gamma)
            skill_threshold: Minimo de reward para ser professor
        """
        self.teaching_cost = teaching_cost
        self.learning_boost = learning_boost
        self.skill_threshold = skill_threshold

        self.lessons_given = 0
        self.total_teaching_cost = 0.0

    def get_name(self) -> str:
        return "Teaching"

    def get_description(self) -> str:
        return "Mentoria entre agentes experientes e novatos"

    def get_params(self) -> Dict[str, Any]:
        return {
            "teaching_cost": self.teaching_cost,
            "learning_boost": self.learning_boost,
            "skill_threshold": self.skill_threshold
        }

    def on_simulation_start(self, runner) -> None:
        self.lessons_given = 0
        self.total_teaching_cost = 0.0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if len(runner.agents) < 2:
            return

        # Identifica professores e alunos
        max_reward = max(tick_rewards) if tick_rewards else 1
        threshold = max_reward * self.skill_threshold

        teachers = [
            (i, a) for i, a in enumerate(runner.agents)
            if i < len(tick_rewards)
            and tick_rewards[i] >= threshold
            and a.balance >= self.teaching_cost
        ]

        students = [
            (i, a) for i, a in enumerate(runner.agents)
            if i < len(tick_rewards)
            and tick_rewards[i] < threshold
        ]

        if not teachers or not students:
            return

        # Cada professor ensina um aluno
        for teacher_idx, teacher in teachers:
            if not students:
                break

            # Escolhe aluno (vizinho se possivel)
            student_neighbors = [
                (i, s) for i, s in students
                if s.node_id in teacher.neighbors
            ]

            if student_neighbors:
                student_idx, student = random.choice(student_neighbors)
            else:
                student_idx, student = random.choice(students)

            # Remove da lista
            students = [(i, s) for i, s in students if i != student_idx]

            # Ensina
            teacher.balance -= self.teaching_cost
            self.total_teaching_cost += self.teaching_cost
            self.lessons_given += 1

            # Transfere conhecimento
            student.P = (1 - self.learning_boost) * student.P + self.learning_boost * teacher.P

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Aulas dadas": self.lessons_given,
            "Custo total ensino": f"{self.total_teaching_cost:.0f}"
        }
