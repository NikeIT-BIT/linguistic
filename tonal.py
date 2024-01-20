from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
import asyncio
import boto3
from boto3.dynamodb.conditions import Attr
from connect import forecast


def get_sentiment(text):
    tokenizer = RegexTokenizer()
    model = FastTextSocialNetworkModel(tokenizer=tokenizer)
    results = model.predict([text], k=2)
    return results[0]


async def main():

    scan = forecast.scan()

    length = 6000
    for i in range(5001, length):
        title = scan['Items'][i]['title']
        text = scan['Items'][i]['text']
        link = scan['Items'][i]['link']
        vip = scan['Items'][i]['vip']

        if vip and vip != "":
            sentiment = get_sentiment(text)
            print(text)
            if 'negative' in sentiment:
                atr = "Новость негативная на: " + str(sentiment['negative'])
            elif 'positive' in sentiment:
                atr = "Новость положительная на: " + str(sentiment['positive'])
            else:
                atr = "Невозможно провести оценку тональности"
        else:
            atr = "Невозможно провести оценку тональности"

        response = forecast.update_item(
            Key={
                'link': link},
            UpdateExpression='set attractions = :a',
            ExpressionAttributeValues={
                ':a': atr
            }
        )

        print(atr)


if __name__ == '__main__':
    asyncio.run(main())
