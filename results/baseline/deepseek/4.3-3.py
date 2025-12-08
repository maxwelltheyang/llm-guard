def custom_middleware(get_response):
    def middleware(request):
        # Assuming request.user is populated with user data
        if 'admin' in request.user.payload and request.user.payload['admin']:
            request.is_admin = True
        else:
            request.is_admin = False

        response = get_response(request)
        return response
    return middleware
