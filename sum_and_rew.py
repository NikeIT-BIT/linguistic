import asyncio
import boto3
from boto3.dynamodb.conditions import Attr
from connect import forecast
import rewriter
import summarizer


async def main():
    scan = forecast.scan()
    length = 1500
    for i in range(1406, length):
        title = scan['Items'][i]['title']
        text = scan['Items'][i]['text']
        link = scan['Items'][i]['link']

        sum_text = await summarizer.summarize(text)
        rewritten_text = await rewriter.rewrite(text)

        response = forecast.update_item(
            Key={
                'link': link},
            UpdateExpression='set annotation = :n,  new_news = :t',
            ExpressionAttributeValues={
                ':n': sum_text,
                ':t': rewritten_text
            }
        )

        print(sum_text)


if __name__ == '__main__':
    asyncio.run(main())