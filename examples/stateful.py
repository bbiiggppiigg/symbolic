from macros.expression import Implies, Match, ActionList, EQ, GT, NEQ, Action
from macros.types import IPAddr, Port
from macros.variables import Input, Output, FreeVariable
from macros.macro import Invariant, Precedence, Reaction

invariants = list()
precedences = list()
reactions = list()

react1 = Reaction(
        Match(
            [
                EQ(
                    Input("ip4Src"),IPAddr("10.0.0.3")
                        )
                ]
            )
        ,    Implies(
            Match(

                [
                    EQ(
                        Input("ip4Src"),
                        IPAddr("10.0.0.1")
                        ),
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
            ),
        Match(
            [
                EQ(
                    Input("ip4Src"),IPAddr("10.0.0.4")
                        )
                ]
            )
)

react2 = Reaction(
        Match(
            [
                EQ(
                    Input("ip4Src"),IPAddr("10.0.0.3")
                    )
                ]
            )
        ,    Implies(
            Match(

                [
                    EQ(
                        Input("ip4Src"),
                        IPAddr("10.0.0.2")
                        ),
                    ]

                ),
            ActionList(
                [
                    Action(
                        [
                            EQ(
                                Output("port_id_out"),
                                Port(1)
                                )
                            ]
                        )
                    ]
                )
            ),
        Match(
            [
                EQ(
                    Input("ip4Src"),IPAddr("10.0.0.4")
                    )
                ]
            )
)



reactions.append(react1)
reactions.append(react2)

#reactions.append(react)
