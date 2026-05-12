from django.contrib import admin
from django.urls import path, include

# Import views from your apps
from authentication.views import loginPage, signup, logout_view, passwordChange
from URLHandler.views import dashboard, generate, home, deleteurl, analytics_dashboard
from home_shorty.views import short_generate, home_shortener

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('signup/', signup, name="signup"),
    path('loginPage/', loginPage, name="loginPage"),
    path('logout/', logout_view, name="logout"),
    path('passwordChange/', passwordChange, name="passwordChange"),

    # URL Handler
    path('', home, name="home"),
    path('dashboard/', dashboard, name="dashboard"),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('generate/', generate, name="generate"),
    path('deleteurl/', deleteurl, name="deleteurl"),
    path('<str:query>/', home, name="home"),

    # Home Shorty
    path('url_shorten/', home_shortener, name="home_shortener"),
    path('shorten/', short_generate, name="shorten"),

    # Other apps
    path('qr_code/', include('qr_code.urls', namespace="qr_code")),
    path('api/', include('api.urls')),
]