from django import forms
from .models import ChatRoom

class LoginForm(forms.Form):
    email = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


<<<<<<< HEAD
class GroupForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['name']
=======
class SignupForm(forms.Form):
    username = forms.CharField(max_length=50, label="Username", required=True)
    first_name = forms.CharField(max_length=30, label="Họ", required=True)
    last_name = forms.CharField(max_length=30, label="Tên", required=True)
    email = forms.EmailField(label="Email", max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu", required=True)

    day_of_birth = forms.IntegerField(label="Ngày sinh", required=True)
    month_of_birth = forms.IntegerField(label="Tháng sinh", required=True)
    year_of_birth = forms.IntegerField(label="Năm sinh", required=True)

    gender = forms.ChoiceField(
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
        label="Giới tính",
        required=True
    )
    study_at = forms.CharField(max_length=200, label="Học tại", required=False)
    working_at = forms.CharField(max_length=200, label="Làm việc tại", required=False)
    bio = forms.CharField(max_length=200, label="Tiểu sử", required=False, widget=forms.Textarea)
>>>>>>> 8885338dfb4cec3d980b36d9e9165771ed4b2fa8
