from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameCountView.as_view(),name='usernamecount'),
    url(r'^$',views.RegisterCreateUserView.as_view()),
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$',views.RegisterPhoneCountAPIView.as_view(),name='phonecount'),
    url(r'^auths/',obtain_jwt_token),
    #/users/infos/
    url(r'^infos/$',views.UserCenterView.as_view()),
    #/users/emails/
    url(r'^emails/$',views.UserEmailView.as_view()),
    # url(r'^emails/$',views.UserCenterEmailView.as_view()),
    url(r'^emails/verification/$',views.UserActiveEmailView.as_view()),
    url(r'^addresses/$',views.AddressCreateAPIView.as_view()),
]