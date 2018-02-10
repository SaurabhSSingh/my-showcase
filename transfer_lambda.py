import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes


def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:754082972614:portfolio_deployed')

    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('portfolio.saurabhshrikantsingh.info')
        build_bucket = s3.Bucket('portfoliobuild.sss.info')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for x in myzip.namelist():
                obj = myzip.open(x)
                portfolio_bucket.upload_fileobj(obj, x, ExtraArgs={'ContentType': mimetypes.guess_type(x)[0]})
                portfolio_bucket.Object(x).Acl().put(ACL='public-read')

        print "Job done!"
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully.")

    except:
        topic.publish(Subject="Portfolio Deployment Unsuccessfull", Message="Unable to Deploy Portfolio.")
        raise
    return 'Hello from Lambda'
