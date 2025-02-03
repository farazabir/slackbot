from urllib.parse import parse_qs
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import os


SLACK_TOKEN = os.getenv('SLACK_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')


@csrf_exempt
def handle_interaction(request):
    if request.method == 'POST':
        try:
            raw_body = request.body.decode('utf-8')
            parsed_body = parse_qs(raw_body)
            payload = json.loads(parsed_body.get('payload', [None])[0])

            if not payload:
                return JsonResponse({'error': 'Empty payload'}, status=400)

            actions = payload.get('actions', [])
            if not actions:
                return JsonResponse({'error': 'No actions in payload'}, status=400)

            action = actions[0]
            action_id = action.get('action_id')
            performance_id = action.get('value')

            if action_id == 'approve_event_button' and performance_id:
                try:
                    api_url = f'https://staging.dragme.io/performances-status/{performance_id}'
                    api_response = requests.put(
                        api_url, json={'is_approved': 1}, timeout=5)
                    api_response.raise_for_status()
                    return JsonResponse({'status': 'Performance set as approved successfully'}, status=200)
                except requests.ConnectionError:
                    return JsonResponse({'error': 'Failed to connect to the backend service'}, status=503)
                except requests.Timeout:
                    return JsonResponse({'error': 'Backend service request timed out'}, status=504)
                except requests.HTTPError as e:
                    return JsonResponse({'error': f'Backend service returned an error: {str(e)}'}, status=502)
                except Exception as e:
                    return JsonResponse({'error': f'Unexpected error when calling backend service: {str(e)}'}, status=500)
            else:
                return JsonResponse({'error': 'Invalid action or missing performance ID'}, status=400)

        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)}')
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        performance_id = data.get('id')
        event_date = data.get('event_date')
        event_name = data.get('event_name')
        location = data.get('location')
        ticket_link = data.get('ticket_link')
        venue_uuid = data.get('venue_uuid')
        img_url = data.get('img_url')
        event_info = data.get('event_info')
        base_price = data.get('base_price')
        age_minimum = data.get('age_minimum')
        currency = data.get('currency')
        ticket_fees = data.get('ticket_fees')
        ticket_limit = data.get('ticket_limit')
        tickets_on_sale = data.get('tickets_on_sale')
        event_time = data.get('event_time')
        provider = data.get('provider')
        artist = data.get('artist')
        user_id = data.get('user_id')

        fields = []

        if performance_id:
            fields.append(
                {"type": "mrkdwn", "text": f"*ID:* {performance_id}"})
        if event_name:
            fields.append(
                {"type": "mrkdwn", "text": f"*Event Name:* {event_name}"})
        if location:
            fields.append(
                {"type": "mrkdwn", "text": f"*Location:* {location}"})
        if event_date:
            fields.append({"type": "mrkdwn", "text": f"*Date:* {event_date}"})
        if ticket_link:
            fields.append(
                {"type": "mrkdwn", "text": f"*Ticket Link:* {ticket_link}"})
        if venue_uuid:
            fields.append(
                {"type": "mrkdwn", "text": f"*Venue UUID:* {venue_uuid}"})
        if img_url:
            fields.append(
                {"type": "mrkdwn", "text": f"*Image URL:* {img_url}"})
        if event_info:
            fields.append(
                {"type": "mrkdwn", "text": f"*Event Info:* {event_info}"})
        if base_price:
            fields.append(
                {"type": "mrkdwn", "text": f"*Base Price:* {base_price}"})
        if age_minimum:
            fields.append(
                {"type": "mrkdwn", "text": f"*Age Minimum:* {age_minimum}"})
        if currency:
            fields.append(
                {"type": "mrkdwn", "text": f"*Currency:* {currency}"})
        if ticket_fees:
            fields.append(
                {"type": "mrkdwn", "text": f"*Ticket Fees:* {ticket_fees}"})
        if ticket_limit:
            fields.append(
                {"type": "mrkdwn", "text": f"*Ticket Limit:* {ticket_limit}"})
        if tickets_on_sale:
            fields.append(
                {"type": "mrkdwn", "text": f"*Tickets on Sale:* {tickets_on_sale}"})
        if event_time:
            fields.append(
                {"type": "mrkdwn", "text": f"*Event Time:* {event_time}"})
        if provider:
            fields.append(
                {"type": "mrkdwn", "text": f"*Provider:* {provider}"})
        if artist:
            fields.append({"type": "mrkdwn", "text": f"*Artist:* {artist}"})
        if user_id:
            fields.append({"type": "mrkdwn", "text": f"*User ID:* {user_id}"})

        # Limit to maximum of 10 fields per Slack block
        max_fields_per_block = 10
        blocks = []
        while len(fields) > 0:
            blocks.append({
                "type": "section",
                "fields": fields[:max_fields_per_block]
            })
            fields = fields[max_fields_per_block:]

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
                }
            ] + blocks + [
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
                            "value": f"{performance_id}",
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
            error_message = f"Failed to send message to Slack. Status code: {response.status_code}, Response: {response.text}"
            print(error_message)
            return JsonResponse({'error': error_message}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
