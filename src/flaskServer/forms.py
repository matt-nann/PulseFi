from flask_wtf import Form, FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField, FieldList, FormField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from .models import User

class RegisterForm(FlaskForm):
    username = StringField(
        'Username', validators=[DataRequired(), Length(min=1, max=25)]
    )
    email = StringField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=3, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
    

class LoginForm(FlaskForm):
    username = StringField('Username') #, [DataRequired()])
    password = PasswordField('Password') #, [DataRequired()])
    guest_login = BooleanField('Login as Guest')
    submit = SubmitField('Sign In')
    
    def validate(self, extra_validators=None):
        if not super().validate():
            return False
        
        if not self.guest_login.data:
            if not self.username.data or not self.password.data:
                if not self.username.data:
                    self.username.errors.append('Please enter a username')
                if not self.password.data:
                    self.password.errors.append('Please enter a password')
                return False
        
        return True

class ForgotForm(FlaskForm):
    email = StringField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )

class PlaylistForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    id = StringField('Id')

class SelectPlaylistsForm(FlaskForm):
    playlists = FieldList(FormField(PlaylistForm), min_entries=1)
    submit = SubmitField('Submit')

    def validate(self, extra_validators=None):
        print('SelectPlaylistsForm.validate()', self.playlists.data)
        return super().validate()