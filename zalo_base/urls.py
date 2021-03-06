from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('404', views.page_404, name='page_404'),
    path('dang-ky-khach-hang', views.regist_payment, name='regist_payment'),
    path('submit_regist_payment', views.submit_regist_payment, name='submit_regist_payment'),
    path('get_client_by_user_id', views.get_client_by_user_id, name='get_client_by_user_id'),
    path('follow_hook', views.follow_hook, name='follow_hook'),

    path('ccos', views.ccos, name='ccos'),
    path('api/ccos', views.api_ccos, name='api_ccos'),
    path('api/message', views.message, name='message'),
    path('test', views.test, name='test'),

    # ============================================================ #
    path('message', views.message, name='message'),
    path('site', views.site, name='site'),
    path('location/<str:zuser_id>', views.location, name='location'),
    path('location_confirm', views.location_confirm, name='location_confirm'),
    path('declare_confirm', views.declare_confirm, name='declare_confirm'),
    path('checkpoint_confirm', views.checkpoint_confirm, name='checkpoint_confirm'),
    path('tkyt/message', views.tkyt_message, name='tkyt_message'),
    path('tkyt_hook', views.tkyt_hook, name='tkyt_hook')
]