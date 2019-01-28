from macros.expression import Implies, Match, ActionList, EQ, GT, NEQ, Action
from macros.types import IPAddr, Port
from macros.variables import Input, Output, FreeVariable, StateVar
from macros.macro import Invariant, Precedence, Reaction

state_var_list = list()
invariants = list()
precedences = list()
reactions = list()

sv= StateVar("block",Port,0)
state_var_list.append(sv)

react1 = Reaction(
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.4"))]),
            ActionList(
                [
                    Action ([EQ(Output("block_out"),Port(1))])
                    
                ]
                
                ),
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.3"))])
        )

react2 = Reaction(
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.3"))]),
            ActionList(
                [
                    Action ([EQ(Output("block_out"),Port(0))])
                    
                ]
                
                ),
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.4"))])
        )


inv = Invariant(
    Implies(
        Match(

            [
                EQ(
                    Input("ip4Src"),
                    IPAddr("10.0.0.1")
                ),
                EQ(
                    Input("block"),
                    Port(0)
                )
            ]

        ),
        ActionList(
            [
                Action(
                    [
                        EQ(
                            Output("port_id_out"),
                            Port(2)
                        )
                    ]
                )
            ]
        )
    )
)
inv2 = Invariant(
    Implies(
        Match(

            [
                EQ(
                    Input("ip4Src"),
                    IPAddr("10.0.0.2")
                ),
                EQ(
                    Input("block"),
                    Port(0)
                )

            ]

        ),
        ActionList(
            [
                Action([EQ(
                    Output("port_id_out"),
                    Port(1)
                )])
            ]
        )

    )
)
invariants.append(inv)
invariants.append(inv2)
reactions.append(react1)
reactions.append(react2)
#reactions.append(react)
