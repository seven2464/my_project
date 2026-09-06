from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = '387013be'
SPARKAI_API_SECRET = 'YWNjNzU0MDFiODg5NDUyM2FlZWM1ZGRl'
SPARKAI_API_KEY = '75e672af2846851ccf0fddbf36af6ca1'
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'

##################################
#需要在pdf.py里通过对检测数据的统计，完成对烽火讯飞提问的token，然后传入ai.py中，进行提问
#最后将获得的结果打印出来，传入pdf中，完成对检测报告的编辑
##################################

def ask_ai(aiquestion):
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [ChatMessage(
        role="user",
        content=aiquestion)]

    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])

    # 对返回的结果进行处理
    text = str(a)
    start = text.find('根据检测数据')
    end = text.find('通过以上措施，有望提高生产线的效率和产品质量。') + len(
        '通过以上措施，有望提高生产线的效率和产品质量。')

    # 获取并返回需要的文本
    extracted_text = text[start:end]
    return extracted_text

