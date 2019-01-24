from macros.expression import Implies, Match, ActionList, EQ, GT, NEQ, Action
from macros.types import IPAddr, Port
from macros.variables import Input, Output, FreeVariable
from macros.macro import Invariant, Precedence, Reaction

invariants = list()
precedences = list()
reactions = list()
inv0 = Invariant(
    ActionList(
        [
            Action([EQ(
                Input("ip4Src"),
                IPAddr("127.0.0.3")
            )])
        ]
    )
)
inv = Invariant(
    Implies(
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
                            Output("ip4Dst_out"),
                            IPAddr("127.0.0.1")
                        )
                    ]
                )
            ]
        )
    )
)
"""
inv3 = Invariant(
    Implies(
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
                            Output("ip4Dst_out"),
                            IPAddr("127.0.0.2")
                        )
                    ]
                )
            ]
        )
    )
)
"""
inv2 = Invariant(
    Implies(
        Match(

            [
                EQ(
                    Input("ip4Src"),
                    IPAddr("127.0.0.1")
                ),
            ]

        ),
        ActionList(
            [

                Action([EQ(
                    IPAddr("127.0.0.1"),
                    IPAddr("127.0.0.1")
                )])
            ]
        )

    )
)

inv3 = Invariant(
    ActionList([
        Action([
            GT(
                Output("port_id_out"),
                Port(127)
            )
        ])
    ])
)
invariants.append(inv)
invariants.append(inv2)
invariants.append(inv3)

react = Reaction(
    Match(

        [
            EQ(
                Input("ethSrc"),
                FreeVariable("X", "Mac")
            ),
            EQ(
                Input("port_id"),
                FreeVariable("P", "Port")
            )
        ]

    ),
    Implies(
        Match(

            [
                EQ(
                    Input("ethDst"),
                    FreeVariable("X", "Mac")
                )
            ]

        ),
        ActionList(

            [
                Action(
                    [
                        EQ(
                            Output("port_id_out"),
                            FreeVariable("P", "Port"))
                        , GT(FreeVariable("P", "Port"), Port(3))
                    ]
                ),
                Action(
                    [
                        NEQ(
                            Output("port_id_out"),
                            Port(3)
                        )
                    ]
                ),
                Action(
                    [
                        GT(Port(5), Port(4))
                    ]
                )
            ]

        )
    ),
    Match(

        [
            EQ(
                IPAddr("127.0.0.1"),
                IPAddr("127.0.0.1")
            )
        ]

    )
)

reactions.append(react)
