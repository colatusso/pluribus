import pandas as pd
from typing import List, Dict
import numpy as np


class Metrics:
    """
    Coleta e gerencia métricas da simulação.

    Registra estatísticas por tick para análise posterior.
    """

    def __init__(self):
        self.records = []

    def record_tick(
        self,
        tick: int,
        mode: str,
        tick_rewards: List[float],
        global_best_reward: float,
        agents_stats: List[Dict]
    ):
        """
        Registra métricas de um tick.

        Args:
            tick: Número do tick
            mode: "hive" ou "local"
            tick_rewards: Rewards individuais deste tick
            global_best_reward: Melhor reward já encontrado
            agents_stats: Lista de stats de cada agente
        """
        # Lida com caso de todos agentes mortos
        if tick_rewards:
            avg_reward = np.mean(tick_rewards)
            max_reward = np.max(tick_rewards)
            min_reward = np.min(tick_rewards)
            std_reward = np.std(tick_rewards)
        else:
            avg_reward = 0.0
            max_reward = 0.0
            min_reward = 0.0
            std_reward = 0.0

        record = {
            "tick": tick,
            "mode": mode,
            "avg_reward": avg_reward,
            "max_reward": max_reward,
            "min_reward": min_reward,
            "std_reward": std_reward,
            "global_best_reward": global_best_reward,
            "num_agents": len(tick_rewards)
        }

        # Adiciona métricas agregadas dos agentes
        if agents_stats:
            total_rewards = [s["total_reward"] for s in agents_stats]
            record["avg_total_reward"] = np.mean(total_rewards)
            record["max_total_reward"] = np.max(total_rewards)
        else:
            record["avg_total_reward"] = 0.0
            record["max_total_reward"] = 0.0

        self.records.append(record)

    def to_dataframe(self) -> pd.DataFrame:
        """Converte registros para DataFrame"""
        return pd.DataFrame(self.records)

    def save_csv(self, filename: str):
        """Salva métricas em CSV"""
        df = self.to_dataframe()
        df.to_csv(filename, index=False)
        print(f"Métricas salvas em: {filename}")

    def print_summary(self):
        """Imprime sumário das métricas"""
        if not self.records:
            print("Nenhuma métrica registrada")
            return

        df = self.to_dataframe()
        print("\n" + "="*60)
        print("SUMÁRIO DA SIMULAÇÃO")
        print("="*60)

        mode = df["mode"].iloc[0]
        num_ticks = len(df)
        num_agents = df["num_agents"].iloc[0]

        print(f"Modo: {mode.upper()}")
        print(f"Ticks: {num_ticks}")
        print(f"Agentes: {num_agents}")
        print()

        print(f"Reward médio final: {df['avg_reward'].iloc[-1]:.2f}")
        print(f"Reward máximo final: {df['max_reward'].iloc[-1]:.2f}")
        print(f"Melhor reward global: {df['global_best_reward'].iloc[-1]:.2f}")
        print()

        # Estatísticas de progresso
        first_100 = df.head(100)["avg_reward"].mean() if len(df) >= 100 else df["avg_reward"].mean()
        last_100 = df.tail(100)["avg_reward"].mean()

        print(f"Avg reward (primeiros 100 ticks): {first_100:.2f}")
        print(f"Avg reward (últimos 100 ticks): {last_100:.2f}")
        print(f"Melhoria: {((last_100 / first_100) - 1) * 100:.1f}%")
        print("="*60 + "\n")
