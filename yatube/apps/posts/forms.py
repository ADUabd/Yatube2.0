from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создания/редактирования поста."""
    
    class Meta:
        model = Post
        fields = ('text', 'image')
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Что у вас нового?'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_text(self):
        """Проверка что текст поста не пуст и не содержит только пробелы."""
        text = self.cleaned_data.get('text', '')
        if not text or not text.strip():
            raise forms.ValidationError('Текст поста не может быть пустым.')
        if len(text.strip()) < 3:
            raise forms.ValidationError('Текст поста должен содержать минимум 3 символа.')
        return text


class CommentForm(forms.ModelForm):
    """Форма создания комментария."""
    
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Написать комментарий...'
            }),
        }
    
    def clean_text(self):
        """Проверка что комментарий не пуст и не содержит только пробелы."""
        text = self.cleaned_data.get('text', '')
        if not text or not text.strip():
            raise forms.ValidationError('Комментарий не может быть пустым.')
        if len(text.strip()) < 1:
            raise forms.ValidationError('Комментарий должен содержать минимум 1 символ.')
        return text
