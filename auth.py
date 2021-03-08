

def requires_auth(f):
    """Creats Decorator from AuthO to only allow logged-in users access to 
    certain paths/routes within the application"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)
    return decorated
