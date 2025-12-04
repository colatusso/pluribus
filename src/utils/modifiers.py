"""
Sistema de modificadores para parametros dos agentes.

Permite que multiplos plugins modifiquem parametros (learning_rate, epsilon, etc)
sem sobrescrever uns aos outros.
"""
from typing import Dict


class ParameterModifier:
    """
    Gerencia modificadores para um parametro especifico.

    Mantem valor base e aplica multiplicadores de varios plugins.
    """

    def __init__(self, base_value: float):
        """
        Args:
            base_value: Valor base original do parametro
        """
        self.base = base_value
        self.multipliers: Dict[str, float] = {}  # plugin_name -> multiplier

    def set_multiplier(self, plugin_name: str, multiplier: float) -> None:
        """
        Define multiplicador para um plugin.

        Args:
            plugin_name: Nome do plugin
            multiplier: Multiplicador (1.0 = sem mudanca)
        """
        self.multipliers[plugin_name] = multiplier

    def remove_multiplier(self, plugin_name: str) -> None:
        """Remove multiplicador de um plugin"""
        if plugin_name in self.multipliers:
            del self.multipliers[plugin_name]

    def get_value(self) -> float:
        """
        Retorna valor efetivo com todos os multiplicadores aplicados.

        Returns:
            base * produto de todos os multiplicadores
        """
        total_mult = 1.0
        for mult in self.multipliers.values():
            total_mult *= mult
        return self.base * total_mult

    def reset(self) -> None:
        """Remove todos os modificadores"""
        self.multipliers.clear()


class AgentModifiers:
    """
    Container para todos os modificadores de um agente.

    Guarda modificadores de learning_rate, epsilon, etc.
    """

    def __init__(self):
        self._modifiers: Dict[str, ParameterModifier] = {}

    def get_modifier(self, param_name: str, base_value: float) -> ParameterModifier:
        """
        Obtem ou cria modificador para um parametro.

        Args:
            param_name: Nome do parametro (ex: 'learning_rate')
            base_value: Valor base se precisar criar

        Returns:
            ParameterModifier para esse parametro
        """
        if param_name not in self._modifiers:
            self._modifiers[param_name] = ParameterModifier(base_value)
        return self._modifiers[param_name]

    def reset_all(self) -> None:
        """Remove todos os modificadores de todos os parametros"""
        for mod in self._modifiers.values():
            mod.reset()
