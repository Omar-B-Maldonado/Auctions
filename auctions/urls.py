from django.urls import path

from . import views

urlpatterns = [
    path(""                              , views.index         , name="index"     ),
    path("login"                         , views.login_view    , name="login"     ),
    path("logout"                        , views.logout_view   , name="logout"    ),
    path("register"                      , views.register      , name="register"  ),
    path("create"                        , views.create_listing, name="create"    ),
    path("listing/<int:listing_id>"      , views.listing       , name="listing"   ),
    path("watchlist"                     , views.watchlist     , name="watchlist" ),
    path("watch/<int:listing_id>"        , views.watch         , name="watch"     ),
    path("category/<str:category_choice>", views.category      , name="category"  ),
]
