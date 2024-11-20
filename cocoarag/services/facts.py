from uuid import uuid4
import yaml
from box import Box

from langchain_core.messages import HumanMessage, SystemMessage

from cocoarag.services.utils import CustomJSONParser, get_model
from cocoarag.models.queries import QueryModel


class ExtractFactsService:
    def __init__(self) -> None:
        with open("cocoarag/configs/prompts.yml", "r") as file:
            self.prompts: Box = Box(yaml.safe_load(file))

        self.model = get_model("gpt-4o-mini")

    def __call__(self, query: QueryModel, language: str = "ru") -> list[str]:
        """Decompose received query on facts and
        embed them.
        """
        system_prompt: str = self.prompts.extraction.get(language)
        parser = CustomJSONParser()

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query.content),
        ]

        chain = self.model | parser

        output = chain.invoke(messages)

        return output["facts"]


if __name__ == "__main__":
    extractor = ExtractFactsService()

    raw = """Линкольн лично направлял военные действия, которые привели к победе над Конфедерацией во время Гражданской войны 1861—1865 годов. Его президентская деятельность привела к усилению исполнительной власти и отмене рабства на территории США. Линкольн включил в состав правительства ряд своих противников и смог привлечь их к работе над общей целью. Президент на всём протяжении войны удерживал Великобританию и другие европейские страны от интервенции. В его президентство построена трансконтинентальная железная дорога, принят Гомстед-акт, решивший аграрный вопрос. Линкольн был выдающимся оратором, его речи вдохновляли северян и являются ярким наследием до сих пор. По окончании войны предложил план умеренной Реконструкции, связанный с национальным согласием и отказом от мести. 14 апреля 1865 года Линкольн был смертельно ранен в театре, став первым убитым президентом США. Согласно общепринятой точке зрения и социальным опросам, он по-прежнему остаётся одним из лучших и самых любимых президентов Америки, хотя во время президентства подвергался суровой критике."""

    query = QueryModel(trace_id=uuid4().hex, content=raw)

    results = extractor(query, language="ru")

    print(results)
