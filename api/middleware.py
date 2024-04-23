from django.http import JsonResponse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Check if the user is not authenticated and the request is not permitted
        if not request.user.is_authenticated and not request.user.is_permitted:
            # Return a JSON response indicating unauthorized action
            return JsonResponse({'error': 'Unauthorized action, login required'}, status=401)
        return response


class AllowMethodsMiddleware:
    def __init__(self, get_response, allowed_methods):
        self.get_response = get_response
        self.allowed_methods = allowed_methods

    def __call__(self, request):
        if request.method not in self.allowed_methods:
            return JsonResponse({'error': 'Method Not Allowed'}, status=405)
        return self.get_response(request)
