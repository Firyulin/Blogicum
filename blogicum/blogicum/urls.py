from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


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
        include(
            'blogicum.auth_urls'
        )
    ),
] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
