from typing import NamedTuple, Mapping, Tuple, TypeVar, Callable
from processes.mdp_refined import MDPRefined
from processes.det_policy import DetPolicy
from algorithms.dp.dp_analytic import DPAnalytic
from algorithms.dp.dp_numeric import DPNumeric
from algorithms.adp import adp
import algorithms.rl_tabular.monte_carlo as mc_tabular
import algorithms.rl_tabular.td0 as td0_tabular
import algorithms.rl_tabular.tdlambda as tdl_tabular
import algorithms.rl_func_approx.monte_carlo as mc_fa
import algorithms.rl_func_approx.td0 as td0_fa
import algorithms.rl_func_approx.tdlambda as tdl_fa
from algorithms.tabular_base import TabularBase
from algorithms.opt_base import OptBase
from algorithms.td_algo_enum import TDAlgorithm
from itertools import groupby
from utils.gen_utils import memoize
import numpy as np
from operator import itemgetter

S = TypeVar('S')


class RunAllAlgorithms(NamedTuple):

    mdp_refined: MDPRefined
    tolerance: float
    first_visit_mc: bool
    softmax: bool
    epsilon: float
    epsilon_half_life: float
    learning_rate: float
    learning_rate_decay: float
    lambd: float
    num_episodes: int
    max_steps: int

    @memoize
    def get_mdp_rep_for_rl_tabular(self):
        return self.mdp_refined.get_mdp_rep_for_rl_tabular()

    def get_all_algorithms(self) -> Mapping[str, OptBase]:
        return {
            "DP Analytic": self.get_dp_analytic(),
            "DP Numeric": self.get_dp_numeric(),
            "ADP": self.get_adp(),
            "Monte Carlo": self.get_monte_carlo(),
            "SARSA": self.get_sarsa(),
            "QLearning": self.get_qlearning(),
            "Expected SARSA": self.get_expected_sarsa(),
            "SARSA Lambda": self.get_sarsa_lambda(),
            "QLearning Lambda": self.get_qlearning_lambda(),
            "Expected SARSA Lambda": self.get_expected_sarsa_lambda()
        }

    def get_all_optimal_policies(self) -> Mapping[str, Callable[[S], A]]:
        return {s: a.get_optimal_det_policy() for s, a in
                self.get_all_algorithms().items()}

    def get_all_optimal_vf_dicts(self) -> Mapping[str, Callable[[S], float]]:
        return {s: a.get_value_func_dict(a.get_optimal_det_policy())
                for s, a in self.get_all_algorithms().items()}

    def get_dp_analytic(self) -> DPAnalytic:
        return DPAnalytic(self.mdp_refined, self.tolerance)

    def get_dp_numeric(self) -> DPNumeric:
        return DPNumeric(self.mdp_refined, self.tolerance)

    def get_dp_numeric(self) -> DPNumeric:
        return DPNumeric(self.mdp_refined, self.tolerance)

    def get_monte_carlo(self) -> MonteCarlo:
        return MonteCarlo(
            self.get_mdp_rep_for_rl_tabular(),
            self.first_visit_mc,
            self.softmax,
            self.epsilon,
            self.epsilon_half_life,
            self.num_episodes,
            self.max_steps
        )

    def get_sarsa(self) -> TD0:
        return TD0(
            self.get_mdp_rep_for_rl_tabular(),
            TDAlgorithm.SARSA,
            self.softmax,
            self.epsilon,
            self.epsilon_half_life,
            self.learning_rate,
            self.learning_rate_decay,
            self.num_episodes,
            self.max_steps
        )

    def get_qlearning(self) -> TD0:
        return TD0(
            self.get_mdp_rep_for_rl_tabular(),
            TDAlgorithm.QLearning,
            self.softmax,
            self.epsilon,
            self.epsilon_half_life,
            self.learning_rate,
            self.learning_rate_decay,
            self.num_episodes,
            self.max_steps
        )

    def get_expected_sarsa(self) -> TD0:
        return TD0(
            self.get_mdp_rep_for_rl_tabular(),
            TDAlgorithm.ExpectedSARSA,
            self.softmax,
            self.epsilon,
            self.epsilon_half_life,
            self.learning_rate,
            self.learning_rate_decay,
            self.num_episodes,
            self.max_steps
        )

    def get_sarsa_lambda(self) -> TDLambda:
        return TDLambda(
            self.get_mdp_rep_for_rl_tabular(),
            TDAlgorithm.SARSA,
            self.softmax,
            self.epsilon,
            self.epsilon_half_life,
            self.learning_rate,
            self.learning_rate_decay,
            self.lambd,
            self.num_episodes,
            self.max_steps
        )

    def get_qlearning_lambda(self) -> TDLambda:
        return TDLambda(
            self.get_mdp_rep_for_rl_tabular(),
            TDAlgorithm.QLearning,
            self.softmax,
            self.epsilon,
            self.epsilon_half_life,
            self.learning_rate,
            self.learning_rate_decay,
            self.lambd,
            self.num_episodes,
            self.max_steps
        )

    def get_expected_sarsa_lambda(self) -> TDLambda:
        return TDLambda(
            self.get_mdp_rep_for_rl_tabular(),
            TDAlgorithm.ExpectedSARSA,
            self.softmax,
            self.epsilon,
            self.epsilon_half_life,
            self.learning_rate,
            self.learning_rate_decay,
            self.lambd,
            self.num_episodes,
            self.max_steps
        )


if __name__ == '__main__':

    from examples.inv_control import InvControl

    ic = InvControl(
        demand_lambda=0.5,
        lead_time=1,
        stockout_cost=49.,
        fixed_order_cost=0.0,
        epoch_disc_factor=0.98,
        order_limit=7,
        space_limit=8,
        throwout_cost=30.,
        stockout_limit=5,
        stockout_limit_excess_cost=30.
    )
    valid = ic.validate_spec()
    mdp_ref_obj = ic.get_mdp_refined()
    this_tolerance = 1e-4
    this_first_visit_mc = True
    this_softmax = True
    this_epsilon = 0.1
    this_epsilon_half_life = 30
    this_learning_rate = 0.1
    this_learning_rate_decay = 1e6
    this_lambd = 0.8
    this_num_episodes = 300
    this_max_steps = 100

    raa = RunAllAlgorithms(
        mdp_refined=mdp_ref_obj,
        tolerance=this_tolerance,
        first_visit_mc=this_first_visit_mc,
        softmax=this_softmax,
        epsilon=this_epsilon,
        epsilon_half_life=this_epsilon_half_life,
        learning_rate=this_learning_rate,
        learning_rate_decay=this_learning_rate_decay,
        lambd=this_lambd,
        num_episodes=this_num_episodes,
        max_steps=this_max_steps
    )

    def crit(x: Tuple[Tuple[int, ...], int]) -> int:
        return sum(x[0])

    for st, mo in raa.get_all_algorithms().items():
        print("Starting %s" % st)
        opt_pol = mo.get_optimal_det_policy().get_state_to_action_map().items()
        print(sorted(
            [(ip, np.mean([float(y) for _, y in v])) for ip, v in
             groupby(sorted(opt_pol, key=crit), key=crit)],
            key=itemgetter(0)
        ))
