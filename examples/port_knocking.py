from macros.expression import Implies, Match, ActionList, EQ, Action, And, NEQ
from macros.macro import Reaction, PrecedenceFactory
from macros.types import IPAddr, Port
from macros.variables import Input, Output

invariants = list()
precedences = list()
reactions = list()
# ip4Src = 10.0.0.3 -> X ( ip4Src = 10.0.0.1 -> port_out =  2)
state_var_list = list()
symbolic_state_var_list = list()
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
                Input("ip4Src"), IPAddr("10.0.0.255")
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
                Input("ip4Src"), IPAddr("10.0.0.255")
            )
        ]
    )
)
#pf  = PrecedenceFactory.get_instance()
plist = [ (
     And(
        [
            EQ(Input("ip4Src"), IPAddr("10.0.0.1")),  
            NEQ(Output("port_id_out"), Port(0))
        ]
    ),
    And(
        [
            EQ(Input("ip4Src"), IPAddr("10.0.0.2")),
            NEQ(Output("port_id_out"), Port(0))
        ]
    )
   
    )] 

"""
pf.insert(
    And(
        [
            EQ(Input("ip4Src"), IPAddr("10.0.0.1")),  
            NEQ(Output("port_id_out"), Port(0))
        ]
    ),
    And(
        [
            EQ(Input("ip4Src"), IPAddr("10.0.0.2")),
            NEQ(Output("port_id_out"), Port(0))
        ]
    )
)

pf.insert(
    And(
        [
            EQ(Input("ip4Src"), IPAddr("10.0.0.2")),  
            NEQ(Output("port_id_out"), Port(0))
        ]
    ),
    And(
        [
            EQ(Input("ip4Src"), IPAddr("10.0.0.3")),
            NEQ(Output("port_id_out"), Port(0))
        ]
    )
)
"""
reactions.append(react1)
reactions.append(react2)
