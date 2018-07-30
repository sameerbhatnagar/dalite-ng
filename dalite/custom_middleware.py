from django.shortcuts import render
from django.template.response import TemplateResponse

class Handler405Middleware(object):

    def process_response(self, request, response):

        if response.status_code == 405:
            message = 'Allowed methods: {allow}'.format(allow=response['Allow'])
            return TemplateResponse(request, "405.html", status=405, context={ 'message' : message }).render()
        else:
            return response
