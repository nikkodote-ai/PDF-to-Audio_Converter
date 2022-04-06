import requests
import PyPDF2

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir


pdf_text = 'sample_text.pdf'
def convert_to_text(pdf_text):

    #TODO 1: Convert text to pdf
    #create an object variable in rb mode
    with open(pdf_text, 'rb') as pdf_file:
        #create a pdf reader
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        #number of pages in the pdf
        num_pages = pdf_reader.getNumPages()
        print(num_pages)
        #get all the pages from the beginning of the pdf to last
        pages = pdf_reader.getPage(num_pages-1)

        #store text
        text = pages.extractText()
        text = text.split('\n')
        text = ''.join(text)
        # print(text)
        with open('converted_to_text.txt', 'w') as output:
            output.writelines(text)
        return text
text_to_convert = convert_to_text(pdf_text)

#TODO 2: Convert the text to pdf

AWSAccessKeyId=os.getenv('AWSAccessKeyId')
AWSSecretKey=os.getenv('AWSSecretKey')
# from https://docs.aws.amazon.com/polly/latest/dg/get-started-what-next.html


# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(aws_access_key_id= AWSAccessKeyId, aws_secret_access_key=AWSSecretKey, region_name = 'ap-southeast-2' )
polly = session.client("polly")

try:
    # Request speech synthesis
    response = polly.synthesize_speech(Text=text_to_convert, OutputFormat="mp3",
                                        VoiceId="Joanna")
except (BotoCoreError, ClientError) as error:
    # The service returned an error, exit gracefully
    print(error)
    sys.exit(-1)

# Access the audio stream from the response
if "AudioStream" in response:
    # Note: Closing the stream is important because the service throttles on the
    # number of parallel connections. Here we are using contextlib.closing to
    # ensure the close method of the stream object will be called automatically
    # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
           output = os.path.join(gettempdir(), "speech.mp3")

           try:
            # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                   file.write(stream.read())
           except IOError as error:
              # Could not write to file, exit gracefully
              print(error)
              sys.exit(-1)

else:
    # The response didn't contain audio data, exit gracefully
    print("Could not stream audio")
    sys.exit(-1)

# Play the audio using the platform's default player
if sys.platform == "win32":
    os.startfile(output)
else:
    # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, output])
