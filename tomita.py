from connect import forecast
import boto3
from bson import ObjectId
from bs4 import BeautifulSoup
import os
from boto3.dynamodb.conditions import Attr

if __name__ == '__main__':

    scan = forecast.scan()
    #print(scan)
    lenght = 6000

    for i in range(3001, lenght):
        link = scan['Items'][i]['link']
        text = scan['Items'][i]['text']


        file = open('/home/serega/tomita-parser/build/bin/input.txt', 'w')
        file.write(text)
        file.close()

        os.chdir('/home/serega/tomita-parser/build/bin')
        os.system('./tomita-parser config.proto')

        sentens = ""
        f = open("/home/serega/tomita-parser/build/bin/output.html", "r")
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
        for tag in soup.find('table').findAll('a'):
            sentens += str("{1}".format(tag.name, tag.text) + " ")
        print(sentens)
        response = forecast.update_item(
            Key={
                'link': link},
            UpdateExpression='set vip= :v',
            ExpressionAttributeValues={
                ':v': sentens
            }
        )
