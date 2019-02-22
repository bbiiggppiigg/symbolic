from macros.expression import Implies, Match, ActionList, EQ, Action, And
from macros.macro import Reaction, PrecedenceFactory
from macros.types import IPAddr, Port
from macros.variables import Input, Output

invariants = list()
precedences = list()
reactions = list()
# ip4Src = 10.0.0.3 -> X ( ip4Src = 10.0.0.1 -> port_out =  2)

react1 = Reaction(
    Match(
        [
            EQ(
                Input("ip4Src"), IPAddr("10.0.0.3")
            )
        ]
    )
    , Implies(
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
                Input("ip4Src"), IPAddr("10.0.0.4")
            )
        ]
    )
)

# ip4Src = 10.0.0.3 -> X ( ip4Src = 10.0.0.2 -> port_out =  1)

react2 = Reaction(
    Match(
        [
            EQ(
                Input("ip4Src"), IPAddr("10.0.0.3")
            )
        ]
    )
    , Implies(
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
                Input("ip4Src"), IPAddr("10.0.0.4")
            )
        ]
    )
)

PrecedenceFactory.get_instance().insert(
    And(
        [EQ(Input("ip4Src"), IPAddr("10.0.0.3"))]
    ),
    And([
        EQ(Input("ip4Src"), IPAddr("10.0.0.1")),
        EQ(Output("port_id_out"), Port(2))
    ]
    )
)
PrecedenceFactory.get_instance().insert(
    And(
        [EQ(Input("ip4Src"), IPAddr("10.0.0.3"))]
    ),
    And([
        EQ(Input("ip4Src"), IPAddr("10.0.0.2")),
        EQ(Output("port_id_out"), Port(1))
    ]
    )
)

reactions.append(react1)
reactions.append(react2)
