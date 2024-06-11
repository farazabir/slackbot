import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

SLACK_TOKEN = os.getenv('SLACK_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')


@csrf_exempt
def handle_interaction(request):
    if request.method == 'POST':
        payload = json.loads(request.POST.get('payload'))
        action_id = payload['actions'][0]['action_id']
        user_id = payload['user']['id']
        response_url = payload['response_url']

        if action_id == 'approve_event_button':

            response = requests.post(response_url, json={
                "text": f"<@{user_id}> approved the event.",
                "replace_original": True
            })

           # POST url for adding approved data
            api_response = requests.post('db url ', json={
                'event': 'approved',
                'user': user_id,
                'details': payload
            })

            return JsonResponse({'status': 'Interaction handled'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_name = data['eventName']
        event_location = data['eventLocation']
        event_date = data['eventDate']
        performers = data['performers']

        message = {
            "channel": SLACK_CHANNEL,
            "text": "New Event Data for verification:",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*New Event Data for verification:*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Event Name:* {event_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Location:* {event_location}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Date:* {event_date}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Performers:* {performers}"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Approve"
                            },
                            "style": "primary",
                            "value": "approve_event",
                            "action_id": "approve_event_button"
                        }
                    ]
                }
            ]
        }

        response = requests.post('https://slack.com/api/chat.postMessage', headers={
            'Authorization': f'Bearer {SLACK_TOKEN}',
            'Content-Type': 'application/json'
        }, data=json.dumps(message))

        if response.status_code == 200 and response.json().get('ok'):
            return JsonResponse({'status': 'Message sent to Slack'})
        else:
            return JsonResponse({'error': 'Failed to send message'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
