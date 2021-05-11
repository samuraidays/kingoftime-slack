# kingoftime-slack
Slackからking of time打刻する

## depoy
```
# pip install slack_bolt
# pip install python-lambda
# export SLACK_SIGNING_SECRET=XXXXXXXXXXXXXXXXXXX
# export SLACK_BOT_TOKEN=XXXXXXXXXXXXXXXX
# lambda deploy --config-file lazy_aws_lambda_config.yaml --requirements requirements.txt --profile <awsクレデンシャルの名前>
```

## コマンド解説
/kot : 出社、退社  
/kot breakin : 休憩開始  
/kot breakout : 休憩終了  

## Slash Command表示  
![キャプチャ](https://user-images.githubusercontent.com/4385484/117884008-17b72480-b2e7-11eb-8acf-71b80d3cac7e.PNG)

## Airtableカラム  
![Employee directory_ Employee_directory - Airtable ](https://user-images.githubusercontent.com/4385484/117884419-90b67c00-b2e7-11eb-9463-5da046585378.png)
