from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from library_app.api import BookViewSet, MemberViewSet, BorrowRecordViewSet
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
router = routers.DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'members', MemberViewSet)
router.register(r'borrowings', BorrowRecordViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library_app.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
