import re
import functools
import atexit
from typing import Callable, Any, List, Tuple

from none import CommandSession
from none.expression import render

from . import baidu_aip


class Instruction:
    __slots__ = ('text', 'avg_score', 'total_compare', 'initial')

    def __init__(self, text: str, *,
                 avg_score: float = 0.00,
                 total_compare: int = 0,
                 initial: bool = False):
        self.text = text
        self.avg_score = avg_score
        self.total_compare = total_compare
        self.initial = initial

    def __repr__(self):
        return f'<Instruction (text={self.text}, ' \
               f'avg_score={self.avg_score}, ' \
               f'total_compare={self.total_compare}, ' \
               f'initial={self.initial})>'


_cancellation_instructions = [
    Instruction('算了，不用了', initial=True),
    Instruction('那不要了吧', initial=True),
    Instruction('那别了吧', initial=True),
    Instruction('那取消吧', initial=True),
]


async def _calc_text_similarity(
        text: str,
        instructions: List[Instruction],
        ok_score: float = 0.70,
        great_score: float = 0.80) -> Tuple[float, bool]:
    max_score = 0.00
    for inst in instructions:
        curr_score = await baidu_aip.text_similarity(text, inst.text)
        max_score = max(max_score, curr_score)
        if curr_score >= ok_score:
            # this is an ok match, update the avg_score
            curr_total_score = \
                inst.avg_score * inst.total_compare + curr_score
            inst.total_compare += 1
            inst.avg_score = curr_total_score / inst.total_compare

            if curr_score >= great_score:
                # this is a great match,
                # we record the text, and make it an instruction
                new_inst = Instruction(text,
                                       avg_score=curr_score,
                                       total_compare=1)
                instructions.append(new_inst)

            # sort the instructions
            instructions.sort(key=lambda x: x.avg_score, reverse=True)

            # remove the instructions with too little avg_score,
            # however keeping the initial ones
            diff_len = len(instructions) - 6
            if diff_len > 0:
                for i in range(len(instructions) - 1, -1, -1):
                    if not instructions[i].initial:
                        del instructions[i]
                    diff_len -= 1
                    if diff_len == 0:
                        break

            # since we are ok, break the for loop
            break
    print(instructions)
    return max_score, max_score >= ok_score


def handle_cancellation(func: Callable) -> Callable:
    """
    Decorate an args parser to handle cancellation instruction
    sent by users.
    """

    @functools.wraps(func)
    async def wrapper(session: CommandSession) -> Any:
        text = session.current_arg_text.strip()
        is_possible_cancellation = False
        for kw in ('算', '别', '不', '取消'):
            if kw in text:
                is_possible_cancellation = True
                break
        if not session.is_first_run and is_possible_cancellation:
            # we are in an interactive session, waiting for user's input
            if re.match(r'[算别不]\S{0,4}了吧?', text) or \
                    re.match(r'取消了?吧?', text):
                match = True
            else:
                _, match = await _calc_text_similarity(
                    text, _cancellation_instructions)
            if match:
                session.finish(
                    render(session.bot.config.SESSION_CANCELLATION_EXPRESSION))
                return
        return await func(session)

    return wrapper
