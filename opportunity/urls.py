from django.urls import path

from opportunity import views

app_name = "api_opportunities"

urlpatterns = [
    path("", views.OpportunityListView.as_view()),
    path("<str:pk>/", views.OpportunityDetailView.as_view()),
    path("comment/<str:pk>/", views.OpportunityCommentView.as_view()),
    path("attachment/<str:pk>/", views.OpportunityAttachmentView.as_view()),
    path("<str:opportunity_id>/tasks/", views.OpportunityTaskListView.as_view()),
    path("tasks/<str:task_id>/", views.OpportunityTaskDetailView.as_view()),
    path("tasks/<str:task_id>/attachments/", views.OpportunityTaskAttachmentView.as_view()),
    path("attachments/<str:attachment_id>/", views.OpportunityTaskAttachmentDeleteView.as_view()),
]
