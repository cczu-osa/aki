from typing import List, Tuple

from . import baidu_aip


class ExampleSentence:
    __slots__ = ('text', 'avg_score', 'total_compare', 'solid')

    def __init__(self, text: str, *,
                 _avg_score: float = 0.00,
                 _total_compare: int = 0,
                 _solid: bool = True):
        self.text = text
        self.avg_score = _avg_score
        self.total_compare = _total_compare
        self.solid = _solid

    def __repr__(self):
        return f'<ExampleSentence (text={self.text}, ' \
               f'avg_score={self.avg_score}, ' \
               f'total_compare={self.total_compare}, ' \
               f'solid={self.solid})>'


async def calc_sentence_similarity(
        sentence: str,
        example_sentences: List[ExampleSentence],
        max_example_sentences: int = 6,
        keep_solid_sentence: bool = True,
        ok_score: float = 0.70,
        great_score: float = 0.80) -> Tuple[float, bool]:
    max_score = 0.00
    for es in example_sentences:
        curr_score = await baidu_aip.text_similarity(sentence, es.text)
        max_score = max(max_score, curr_score)
        if curr_score >= ok_score:
            # this is an ok match, update the average score
            curr_total_score = \
                es.avg_score * es.total_compare + curr_score
            es.total_compare += 1
            es.avg_score = curr_total_score / es.total_compare

            if curr_score >= great_score:
                # this is a great match,
                # we record the text, and make it an example sentence
                new_es = ExampleSentence(sentence,
                                         _avg_score=curr_score,
                                         _total_compare=1,
                                         _solid=False)
                example_sentences.append(new_es)

            # sort the example sentences to make sure
            # the most possible sentence will be checked first
            example_sentences.sort(key=lambda x: x.avg_score, reverse=True)

            # remove the example sentences with too little average score,
            # however keeping the solid ones if needed
            diff_len = len(example_sentences) - max_example_sentences
            if diff_len > 0:
                for i in range(len(example_sentences) - 1, -1, -1):
                    if not (keep_solid_sentence and
                            example_sentences[i].solid):
                        del example_sentences[i]
                    diff_len -= 1
                    if diff_len == 0:
                        break

            # since we are ok, break the for loop
            break

    return max_score, max_score >= ok_score
