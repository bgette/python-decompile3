#  Copyright (c) 2019-2021 by Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Isolate Python 3.8 version-specific semantic actions here.
"""

########################
# Python 3.8+ changes
#######################

from decompyle3.semantics.consts import PRECEDENCE, TABLE_DIRECT


def customize_for_version38(self, version):

    # FIXME: pytest doesn't add proper keys in testing. Reinstate after we have fixed pytest.
    # for lhs in 'for forelsestmt forelselaststmt '
    #             'forelselaststmtc tryfinally38'.split():
    #     del TABLE_DIRECT[lhs]

    TABLE_DIRECT.update(
        {
            "async_for_stmt38": (
                "%|async for %c in %c:\n%+%c%-%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
            ),
            "async_forelse_stmt38": (
                "%|async for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                (-1, "else_suite"),
            ),
            "async_with_stmt38": ("%|async with %c:\n%+%|%c%-", (0, "expr"), 7),
            "async_with_as_stmt38": (
                "%|async with %c as %c:\n%+%|%c%-",
                (0, "expr"),
                (6, "store"),
                (7, "suite_stmts"),
            ),
            "c_forelsestmt38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -1,
            ),
            "except_cond1a": ("%|except %c:\n", (1, "expr"),),
            "except_cond_as": (
                "%|except %c as %c:\n",
                (1, "expr"),
                (-2, "STORE_FAST"),
            ),
            "except_handler38": ("%c", (2, "except_stmts")),
            "except_handler38a": ("%c", (-2, "stmts")),
            "except_handler38c": (
                "%c%+%c%-",
                (1, "except_cond1a"),
                (2, "except_stmts"),
            ),
            "except_handler_as": (
                "%c%+\n%+%c%-",
                (1, "except_cond_as"),
                (2, "tryfinallystmt"),
            ),
            "except_ret38a": ("return %c", (4, "expr")),
            # Note: there is a suite_stmts_opt which seems
            # to be bookkeeping which is not expressed in source code
            "except_ret38": ("%|return %c\n", (1, "expr")),
            "for38": (
                "%|for %c in %c:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
            ),
            "forelsestmt38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -1,
            ),
            "forelselaststmt38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -2,
            ),
            "forelselaststmtc38": (
                "%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n",
                (2, "store"),
                (0, "expr"),
                (3, "for_block"),
                -2,
            ),
            "ifpoplaststmtc": ("%|if %c:\n%+%c%-", (0, "testexpr"), (2, "c_stmts")),
            "pop_return": ("%|return %c\n", (1, "ret_expr")),
            "popb_return": ("%|return %c\n", (0, "ret_expr")),
            "pop_ex_return": ("%|return %c\n", (0, "ret_expr")),
            "whilestmt38": (
                "%|while %c:\n%+%c%-\n\n",
                (1, "testexpr"),
                (2, ("c_stmts", "pass")),
            ),
            "whileTruestmt38": ("%|while True:\n%+%c%-\n\n", (1, "c_stmts", "pass"),),
            "try_elsestmtl38": (
                "%|try:\n%+%c%-%c%|else:\n%+%c%-",
                (1, "suite_stmts_opt"),
                (3, "except_handler38"),
                (5, "else_suitec"),
            ),
            "try_except38": (
                "%|try:\n%+%c\n%-%|except:\n%+%c%-\n\n",
                (2, ("suite_stmts_opt", "suite_stmts")),
                (3, ("except_handler38a", "except_handler38b", "except_handler38c")),
            ),
            "try_except38r": (
                "%|try:\n%+%c\n%-%|except:\n%+%c%-\n\n",
                (1, "return_except"),
                (2, "except_handler38b"),
            ),
            "try_except38r2": (
                "%|try:\n%+%c\n%-%|except:\n%+%c%c%-\n\n",
                (1, "suite_stmts_opt"),
                (8, "cond_except_stmts_opt"),
                (10, "return"),
            ),
            "try_except_as": (
                "%|try:\n%+%c%-\n%|%-%c\n\n",
                (-4, "suite_stmts"),  # Go from the end because of POP_BLOCK variation
                (-3, "except_handler_as"),
            ),
            "try_except_ret38": (
                "%|try:\n%+%c%-\n%|except:\n%+%|%c%-\n\n",
                (1, "returns"),
                (2, "except_ret38a"),
            ),
            "try_except_ret38a": (
                "%|try:\n%+%c%-%c\n\n",
                (1, "returns"),
                (2, "except_handler38c"),
            ),
            "tryfinally38rstmt": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (0, "sf_pb_call_returns"),
                (-1, ("ss_end_finally", "suite_stmts")),
            ),
            "tryfinally38rstmt2": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (4, "returns"),
                -2,
                "ss_end_finally",
            ),
            "tryfinally38rstmt3": (
                "%|try:\n%+%|return %c%-\n%|finally:\n%+%c%-\n\n",
                (1, "expr"),
                (-1, "ss_end_finally"),
            ),
            "tryfinally38rstmt4": (
                "%|try:\n%+%c%-\n%|finally:\n%+%c%-\n\n",
                (1, "suite_stmts_opt"),
                (5, "suite_stmts_return"),
            ),
            "tryfinally38stmt": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (1, "suite_stmts_opt"),
                (6, "suite_stmts_opt"),
            ),
            "tryfinally38astmt": (
                "%|try:\n%+%c%-%|finally:\n%+%c%-\n\n",
                (2, "suite_stmts_opt"),
                (8, "suite_stmts_opt"),
            ),
            "named_expr": (  # AKA "walrus operator"
                "%c := %p",
                (2, "store"),
                (0, "expr", PRECEDENCE["named_expr"] - 1),
            ),
        }
    )

    # FIXME: now that we've split out cond_except_stmt,
    # we should be able to get this working as a pure transformation rule,
    # so no procedure is needed here.
    def try_except38r3(node):
        self.template_engine(("%|try:\n%+%c\n%-", (1, "suite_stmts_opt")), node)
        cond_except_stmts_opt = node[5]
        assert cond_except_stmts_opt == "cond_except_stmts_opt"
        for child in cond_except_stmts_opt:
            if child == "cond_except_stmt":
                if child[0] == "except_cond1":
                    self.template_engine(
                        ("%c\n", (0, "except_cond1"), (1, "expr")), child
                    )
                    self.template_engine(("%+%c%-\n", (1, "except_stmts")), child)
                pass
            pass
        self.template_engine(("%+%c%-\n", (7, "return")), node)
        self.prune()

    self.n_try_except38r3 = try_except38r3

    def suite_stmts_return(node):
        if len(node) > 1:
            assert len(node) == 2
            self.template_engine(
                ("%c\n%|return %c", (0, "suite_stmts"), (1, "expr")), node
            )
        else:
            self.template_engine(("%|return %c", (0, "expr")), node)
        self.prune()

    self.n_suite_stmts_return = suite_stmts_return
