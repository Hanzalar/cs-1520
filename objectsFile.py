class User(object):
    def __init__(self, name, password, email, bio=None):
        self.name = name
        self.password = password
        self.email = email
        if bio:
            self.bio = bio
        else:
            self.bio = None
        
    def get(self):
        dict = {
            'user' : self.name,
            'password' : self.password,
            'email' : self.email,
            'bio' : self.bio
        }

        return dict