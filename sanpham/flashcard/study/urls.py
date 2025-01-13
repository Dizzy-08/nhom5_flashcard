from django.urls import path
from . import views

urlpatterns = [
    path("start/<int:deck_id>/", views.start_study_session, name="start_study_session"),
    path("session/<int:session_id>/", views.study_session, name="study_session"),
    # path("session/<int:session_id>/update/<int:card_id>/",views.update_card_progress,name="update_card_progress",),
    path(
        "session/<int:session_id>/check_answer/",
        views.check_answer,
        name="check_answer",
    ),
]
