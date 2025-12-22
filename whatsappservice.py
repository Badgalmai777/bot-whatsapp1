import requests
import json


def SendMessageWhatsapp(data):
    try:
        token = "EAATXdl1KmQkBQIZB2hmynmZBI0VlBQdV9MkOrld5gT8ZCEaSNAWwYUVnZAvTcM2ng1laGna74y9BPaSYDZAiGa0dSBJhV2mMhB7we0K4Nys1oS5No8oYBHggnxNGUriS0Jx4kGHy0EZAwo2AE1m4zQuUwFj3hkMC7NsctrG7fXZCvDZAfztomsm2eZCCqPwuPZAqNDZAILZCI4LLiJPJFw7lZCglDVsFOM9ZAvJfuogwvZAz6YW"
        api_url = "https://graph.facebook.com/v22.0/895387210323476/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        }
        response = requests.post(api_url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return True

        return False
    except Exception as exception:
        print(exception)
        return False
