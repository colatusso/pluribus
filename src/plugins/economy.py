"""
Plugins de economia para Pluribus.

Implementam mecanismos de mercado, impostos e investimentos.
"""
import random
import numpy as np
from typing import Dict, Any, List, Set, Tuple
from .base import Plugin


class MarketPlugin(Plugin):
    """
    Mercado de informacao - agentes compram e vendem hints.

    Agentes com bom progresso podem vender informacao sobre
    posicoes que acertaram. Preco dinamico baseado em oferta/demanda.

    Cria economia de conhecimento.
    """

    priority = 25
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        base_price: float = 10.0,
        price_volatility: float = 0.2,
        info_quality: float = 0.8
    ):
        """
        Args:
            base_price: Preco base de uma hint
            price_volatility: Variacao de preco por tick
            info_quality: Qualidade da info vendida (chance de ser correta)
        """
        self.base_price = base_price
        self.price_volatility = price_volatility
        self.info_quality = info_quality

        self.current_price = base_price
        self.transactions = 0
        self.total_volume = 0.0

    def get_name(self) -> str:
        return "Market"

    def get_description(self) -> str:
        return "Mercado de compra e venda de informacao"

    def get_params(self) -> Dict[str, Any]:
        return {
            "base_price": self.base_price,
            "price_volatility": self.price_volatility,
            "info_quality": self.info_quality
        }

    def on_simulation_start(self, runner) -> None:
        self.current_price = self.base_price
        self.transactions = 0
        self.total_volume = 0.0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if len(runner.agents) < 2:
            return

        # Ajusta preco baseado em demanda
        demand = sum(1 for r in tick_rewards if r < 50) / len(tick_rewards)
        self.current_price *= (1 + (demand - 0.5) * self.price_volatility)
        self.current_price = max(1.0, self.current_price)

        # Identifica vendedores (agentes com bom progresso) e compradores
        sellers = [(i, a) for i, a in enumerate(runner.agents)
                   if i < len(tick_rewards) and tick_rewards[i] >= 50]
        buyers = [(i, a) for i, a in enumerate(runner.agents)
                  if i < len(tick_rewards) and tick_rewards[i] < 50
                  and a.balance >= self.current_price]

        # Realiza transacoes
        for buyer_idx, buyer in buyers:
            if not sellers:
                break

            # Escolhe vendedor aleatorio
            seller_idx, seller = random.choice(sellers)

            # Transacao
            if buyer.balance >= self.current_price:
                buyer.balance -= self.current_price
                seller.balance += self.current_price * 0.9  # 10% taxa
                self.transactions += 1
                self.total_volume += self.current_price

                # Transfere informacao (com qualidade)
                if random.random() < self.info_quality:
                    self._transfer_knowledge(seller, buyer)

    def _transfer_knowledge(self, seller, buyer) -> None:
        """Transfere conhecimento do vendedor para comprador"""
        # Mistura policies com peso no vendedor
        gamma = 0.3
        buyer.P = (1 - gamma) * buyer.P + gamma * seller.P

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Transacoes": self.transactions,
            "Volume total": f"{self.total_volume:.0f}",
            "Preco final": f"{self.current_price:.1f}"
        }


class TaxPlugin(Plugin):
    """
    Sistema de impostos e redistribuicao.

    Agentes ricos pagam imposto progressivo que e redistribuido
    para agentes pobres. Simula welfare state.

    Pode ser configurado de liberal (sem imposto) a socialista (alto).
    """

    priority = 30
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        tax_rate: float = 0.1,
        threshold_multiplier: float = 1.5,
        redistribution: str = "equal"
    ):
        """
        Args:
            tax_rate: Taxa de imposto sobre excesso (0-1)
            threshold_multiplier: Multiplica media para definir limite de taxacao
            redistribution: "equal" (igual) ou "proportional" (proporcional a necessidade)
        """
        self.tax_rate = tax_rate
        self.threshold_multiplier = threshold_multiplier
        self.redistribution = redistribution

        self.total_collected = 0.0
        self.total_distributed = 0.0

    def get_name(self) -> str:
        return "Tax"

    def get_description(self) -> str:
        return "Impostos progressivos com redistribuicao"

    def get_params(self) -> Dict[str, Any]:
        return {
            "tax_rate": self.tax_rate,
            "threshold_multiplier": self.threshold_multiplier,
            "redistribution": self.redistribution
        }

    def on_simulation_start(self, runner) -> None:
        self.total_collected = 0.0
        self.total_distributed = 0.0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents:
            return

        # Calcula media de balance
        avg_balance = sum(a.balance for a in runner.agents) / len(runner.agents)
        threshold = avg_balance * self.threshold_multiplier

        # Coleta impostos dos ricos
        collected = 0.0
        for agent in runner.agents:
            if agent.balance > threshold:
                excess = agent.balance - threshold
                tax = excess * self.tax_rate
                agent.balance -= tax
                collected += tax

        self.total_collected += collected

        if collected <= 0:
            return

        # Identifica pobres (abaixo da media)
        poor = [a for a in runner.agents if a.balance < avg_balance]
        if not poor:
            return

        # Distribui
        if self.redistribution == "equal":
            share = collected / len(poor)
            for agent in poor:
                agent.balance += share
        else:  # proportional
            total_need = sum(avg_balance - a.balance for a in poor)
            if total_need > 0:
                for agent in poor:
                    need = avg_balance - agent.balance
                    share = collected * (need / total_need)
                    agent.balance += share

        self.total_distributed += collected

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Imposto coletado": f"{self.total_collected:.0f}",
            "Redistribuido": f"{self.total_distributed:.0f}",
            "Metodo": self.redistribution
        }


class InvestmentPlugin(Plugin):
    """
    Sistema de investimento com juros.

    Agentes podem investir parte do balance para ganhar juros,
    mas ficam sem esse recurso para tentativas.

    Equilibra risco vs seguranca financeira.
    """

    priority = 35
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        interest_rate: float = 0.02,
        min_investment: float = 50.0,
        investment_ratio: float = 0.3
    ):
        """
        Args:
            interest_rate: Taxa de juros por tick
            min_investment: Minimo para investir
            investment_ratio: Fracao do balance que agentes investem
        """
        self.interest_rate = interest_rate
        self.min_investment = min_investment
        self.investment_ratio = investment_ratio

        # Investimentos por agente
        self.investments: Dict[int, float] = {}
        self.total_interest_paid = 0.0

    def get_name(self) -> str:
        return "Investment"

    def get_description(self) -> str:
        return "Investimentos com juros compostos"

    def get_params(self) -> Dict[str, Any]:
        return {
            "interest_rate": self.interest_rate,
            "min_investment": self.min_investment,
            "investment_ratio": self.investment_ratio
        }

    def on_simulation_start(self, runner) -> None:
        self.investments = {}
        self.total_interest_paid = 0.0

        # Investimento inicial
        for agent in runner.agents:
            investment = agent.balance * self.investment_ratio
            if investment >= self.min_investment:
                agent.balance -= investment
                self.investments[agent.node_id] = investment

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        # Aplica juros
        for agent in runner.agents:
            if agent.node_id in self.investments:
                investment = self.investments[agent.node_id]
                interest = investment * self.interest_rate
                self.investments[agent.node_id] += interest
                self.total_interest_paid += interest

        # Agentes em dificuldade resgatam investimento
        for agent in runner.agents:
            if agent.balance <= agent.cost_per_attempt * 2:
                if agent.node_id in self.investments:
                    # Resgata
                    agent.balance += self.investments[agent.node_id]
                    del self.investments[agent.node_id]

    def on_simulation_end(self, runner) -> None:
        # Resgata todos os investimentos
        for agent in runner.agents:
            if agent.node_id in self.investments:
                agent.balance += self.investments[agent.node_id]

    def get_stats(self) -> Dict[str, Any]:
        total_invested = sum(self.investments.values())
        return {
            "Total investido": f"{total_invested:.0f}",
            "Juros pagos": f"{self.total_interest_paid:.0f}",
            "Investidores ativos": len(self.investments)
        }
