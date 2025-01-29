from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.internal_error'

urlpatterns = [
    path(
        'admin/',
        admin.site.urls
    ),
    path(
        'pages/',
        include(
            'pages.urls'
        )
    ),
    path(
        '',
        include(
            'blog.urls'
        )
    ),
    path(
        'auth/',
        include(
            'django.contrib.auth.urls'
        )
    ),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
]
