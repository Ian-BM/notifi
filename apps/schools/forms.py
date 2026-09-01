from django import forms

from .models import School


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            'name', 'phone', 'email', 'contact_person', 'address',
            'sender_id', 'sender_id_status', 'is_active', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'sender_id': forms.TextInput(attrs={'class': 'form-input', 'maxlength': 11}),
            'sender_id_status': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class SchoolUserForm(forms.Form):
    username = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=False,
        help_text='Leave blank to auto-generate a password.',
    )
