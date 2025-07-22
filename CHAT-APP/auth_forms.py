from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username or Email', 
                          validators=[DataRequired(), Length(min=3, max=80)],
                          render_kw={"placeholder": "Enter your username or email", "class": "form-control"})
    password = PasswordField('Password', 
                            validators=[DataRequired()],
                            render_kw={"placeholder": "Enter your password", "class": "form-control"})
    remember_me = BooleanField('Remember Me', render_kw={"class": "form-check-input"})
    submit = SubmitField('Sign In', render_kw={"class": "btn btn-primary w-100"})

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80)],
                          render_kw={"placeholder": "Choose a username", "class": "form-control"})
    email = StringField('Email', 
                       validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "Enter your email address", "class": "form-control"})
    first_name = StringField('First Name', 
                            validators=[Length(max=50)],
                            render_kw={"placeholder": "First name (optional)", "class": "form-control"})
    last_name = StringField('Last Name', 
                           validators=[Length(max=50)],
                           render_kw={"placeholder": "Last name (optional)", "class": "form-control"})
    password = PasswordField('Password', 
                            validators=[DataRequired(), Length(min=6, max=128)],
                            render_kw={"placeholder": "Create a strong password", "class": "form-control"})
    password_confirm = PasswordField('Confirm Password',
                                   validators=[DataRequired(), EqualTo('password', message='Passwords must match')],
                                   render_kw={"placeholder": "Confirm your password", "class": "form-control"})
    submit = SubmitField('Create Account', render_kw={"class": "btn btn-success w-100"})
    
    def validate_username(self, username):
        """Check if username already exists"""
        from auth_models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        from auth_models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or sign in.')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', 
                           validators=[DataRequired(), Length(min=1, max=1000)],
                           render_kw={"placeholder": "Type your secure message here...", 
                                     "class": "form-control", 
                                     "rows": "4",
                                     "maxlength": "1000"})
    submit = SubmitField('Send Encrypted Message', render_kw={"class": "btn btn-primary w-100"})

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', 
                            validators=[Length(max=50)],
                            render_kw={"placeholder": "First name", "class": "form-control"})
    last_name = StringField('Last Name', 
                           validators=[Length(max=50)],
                           render_kw={"placeholder": "Last name", "class": "form-control"})
    email = StringField('Email', 
                       validators=[DataRequired(), Email()],
                       render_kw={"class": "form-control"})
    submit = SubmitField('Update Profile', render_kw={"class": "btn btn-primary"})
    
    def __init__(self, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """Check if email already exists (excluding current user)"""
        if email.data != self.original_email:
            from auth_models import User
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email.')