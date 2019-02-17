from macros.expression import Implies, Match, ActionList, EQ, GT, NEQ, Action
from macros.types import IPAddr, Port , Bool
from macros.variables import Input, Output, FreeVariable, StateVar, SymbolicStateVar
from macros.macro import Invariant, Precedence, Reaction

state_var_list = list()
invariants = list()
precedences = list()
reactions = list()

symbolic_state_var_list=  list()

sv= StateVar("block",Bool,False)
state_var_list.append(sv)
ssv = SymbolicStateVar("learnt",IPAddr,Bool,False)
symbolic_state_var_list.append(ssv)
tt = Invariant( 
    Implies(
        Match(
            [
            EQ(Input("ip4Dst"),FreeVariable("X","IPAddr")),
            EQ(Input("learnt",FreeVariable("X","IPAddr")),Bool(False))
            ]
        ),
        ActionList(
            [
                Action([
                    EQ(
                        Output("port_id_out"),
                        Port(100)
                        )
                    ]) 
            ]    
        )
    )
)

tt2 = Invariant( 
    Implies(
        Match(
            [
            EQ(Input("ip4Src"),FreeVariable("X","IPAddr")),
            ]
        ),
        ActionList(
            [
                Action([
                    EQ(
                        Output("learnt_out",FreeVariable("X","IPAddr")),
                        Bool(True)
                        )
                    ]) 
            ]    
        )
    )
)


react1 = Reaction(
            Match([
                EQ(Input("ip4Src"),FreeVariable("X","IPAddr")),
                EQ(Input("port_id"),FreeVariable("Y","Port")),
                ]),
            
            Implies(
                Match(
                    [
                        EQ(Input("ip4Dst"),FreeVariable("X","IPAddr"))
                    ]
                ),
                ActionList(
                    [
                        Action(
                            [
                                EQ(
                                    Output("port_id_out"),
                                    FreeVariable("Y","Port")
                                )
                            ]
                            )
                    ]
                )
            )
            ,
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.3"))])
)


"""
react1 = Reaction(
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.4"))]),
            ActionList(
                [
                    Action ([EQ(Output("block_out"),Bool(True))])
                    
                ]
                
                ),
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.3"))])
        )

react2 = Reaction(
            Match([EQ(Input("ip4Src"),IPAddr("10.0.0.3"))]),
            ActionList(
                [
                    Action ([EQ(Output("block_out"),Bool(False))])
                    
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
                    Bool(False)
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
                    Bool(False)
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
"""
invariants.append(tt)
invariants.append(tt2)

#precedences.append(prec1)
#invariants.append(inv)
#invariants.append(inv2)
reactions.append(react1)
#reactions.append(react2)
#reactions.append(react)
