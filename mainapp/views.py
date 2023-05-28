from django.shortcuts import redirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline')
        request.session['state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        state = request.session.pop('state', '')
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
            state=state
        )
        flow.fetch_token(code=request.GET.get('code'))
        credentials = flow.credentials
        service = build('calendar', 'v3', credentials=credentials)
        events = service.events().list(calendarId='primary').execute()
        return Response(events)
