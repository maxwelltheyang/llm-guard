class UserMiddleware:
    def __init__(self, get_user):
        self.get_user = get_user

    def __call__(self, handler):
        def wrapper(request):
            user = self.get_user()
            if hasattr(user, 'admin') and user.admin:
                request.__dict__['user_admin'] = user.admin
            return handler(request)
        return wrapper
