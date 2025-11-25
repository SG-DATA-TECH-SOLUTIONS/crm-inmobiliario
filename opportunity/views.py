import json

from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account, Tags
from accounts.serializer import AccountSerializer, TagsSerailizer
from common.models import Attachments, Comment, Profile

#from common.external_auth import CustomDualAuthentication
from common.serializer import (
    AttachmentsSerializer,
    CommentSerializer,
    ProfileSerializer,
)
from common.utils import CURRENCY_CODES, SOURCES, STAGES
from contacts.models import Contact
from contacts.serializer import ContactSerializer
from opportunity import swagger_params1
from opportunity.models import Opportunity
from opportunity.serializer import *
from opportunity.tasks import send_email_to_assigned_user
from opportunity.constants import OpportunityStages
from teams.models import Teams


# ============================================================================
# OPPORTUNITY TASK CONFIGURATION
# Edit this to customize default tasks and deadlines for each stage
# ============================================================================
DEFAULT_OPPORTUNITY_TASKS = {
    OpportunityStages.STAGE_1: [
        {'name': 'Initial contact and needs assessment'},
        {'name': 'Identify key stakeholders', 'deadline_days': 5},
        {'name': 'Document requirements', 'deadline_days': 7},
    ],
    OpportunityStages.STAGE_2: [
        {'name': 'Prepare proposal draft'},
        {'name': 'Review with team', 'deadline_days': 5},
        {'name': 'Submit proposal to client', 'deadline_days': 7},
    ],
    OpportunityStages.STAGE_3: [
        {'name': 'Address client feedback', 'deadline_days': 3},
        {'name': 'Finalize terms and pricing', 'deadline_days': 5},
        {'name': 'Prepare contract', 'deadline_days': 7},
    ],
}
# ============================================================================


class OpportunityListView(APIView, LimitOffsetPagination):

    #authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Opportunity

    def get_context_data(self, **kwargs):
        params = self.request.query_params
        queryset = self.model.objects.filter(org=self.request.profile.org).order_by("-id")
        accounts = Account.objects.filter(org=self.request.profile.org)
        contacts = Contact.objects.filter(org=self.request.profile.org)
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(created_by=self.request.profile.user) | Q(assigned_to=self.request.profile)
            ).distinct()
            accounts = accounts.filter(
                Q(created_by=self.request.profile.user) | Q(assigned_to=self.request.profile)
            ).distinct()
            contacts = contacts.filter(
                Q(created_by=self.request.profile.user) | Q(assigned_to=self.request.profile)
            ).distinct()

        if params:
            if params.get("name"):
                queryset = queryset.filter(name__icontains=params.get("name"))
            if params.get("account"):
                queryset = queryset.filter(account=params.get("account"))
            if params.get("stage"):
                queryset = queryset.filter(stage__contains=params.get("stage"))
            if params.get("lead_source"):
                queryset = queryset.filter(
                    lead_source__contains=params.get("lead_source")
                )
            if params.get("tags"):
                queryset = queryset.filter(
                    tags__in=params.get("tags")
                ).distinct()

        context = {}
        results_opportunities = self.paginate_queryset(
            queryset.distinct(), self.request, view=self
        )
        opportunities = OpportunitySerializer(results_opportunities, many=True).data
        if results_opportunities:
            offset = queryset.filter(id__gte=results_opportunities[-1].id).count()
            if offset == queryset.count():
                offset = None
        else:
            offset = 0
        context["per_page"] = 10
        page_number = (int(self.offset / 10) + 1,)
        context["page_number"] = page_number
        context.update(
            {
                "opportunities_count": self.count,
                "offset": offset,
            }
        )
        context["opportunities"] = opportunities
        context["accounts_list"] = AccountSerializer(accounts, many=True).data
        context["contacts_list"] = ContactSerializer(contacts, many=True).data
        context["tags"] = TagsSerailizer(Tags.objects.filter(), many=True).data
        context["stage"] = STAGES
        context["lead_source"] = SOURCES
        context["currency"] = CURRENCY_CODES

        return context

    @extend_schema(
        tags=["Opportunities"],
        parameters=swagger_params1.opportunity_list_get_params,
    )
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return Response(context)

    @extend_schema(
        tags=["Opportunities"],
        parameters=swagger_params1.organization_params,request=OpportunityCreateSwaggerSerializer
    )
    def post(self, request, *args, **kwargs):
        params = request.data
        serializer = OpportunityCreateSerializer(data=params, request_obj=request)
        if serializer.is_valid():
            # Convert empty string to None for due_date
            due_date = params.get("due_date")
            if due_date == "" or due_date is None:
                due_date = None
            
            opportunity_obj = serializer.save(
                created_by=request.profile.user,
                closed_on=due_date,
                org=request.profile.org,
            )

            if params.get("contacts"):
                contacts_list = params.get("contacts")
                contacts = Contact.objects.filter(id__in=contacts_list, org=request.profile.org)
                opportunity_obj.contacts.add(*contacts)

            if params.get("tags"):
                tags = params.get("tags")
                for tag in tags:
                    obj_tag = Tags.objects.filter(slug=tag.lower())
                    if obj_tag.exists():
                        obj_tag = obj_tag[0]
                    else:
                        obj_tag = Tags.objects.create(name=tag)
                    opportunity_obj.tags.add(obj_tag)

            if params.get("stage"):
                stage = params.get("stage")
                if stage in ["CLOSED WON", "CLOSED LOST"]:
                    opportunity_obj.closed_by = self.request.profile

            if params.get("teams"):
                teams_list = params.get("teams")
                teams = Teams.objects.filter(id__in=teams_list, org=request.profile.org)
                opportunity_obj.teams.add(*teams)

            if params.get("assigned_to"):
                assinged_to_list = params.get("assigned_to")
                profiles = Profile.objects.filter(
                    id__in=assinged_to_list, org=request.profile.org, is_active=True
                )
                opportunity_obj.assigned_to.add(*profiles)

            if self.request.FILES.get("opportunity_attachment"):
                attachment = Attachments()
                attachment.created_by = self.request.profile.user
                attachment.file_name = self.request.FILES.get(
                    "opportunity_attachment"
                ).name
                attachment.opportunity = opportunity_obj
                attachment.attachment = self.request.FILES.get("opportunity_attachment")
                attachment.save()

            # Create default tasks for all stages
            try:
                from opportunity.models import OpportunityTask
                from datetime import timedelta
                from django.utils import timezone
                
                now = timezone.now()
                
                # Create tasks from configuration
                for stage, tasks in DEFAULT_OPPORTUNITY_TASKS.items():
                    for order, task_config in enumerate(tasks, start=1):
                        # Only first stage gets deadlines on creation
                        deadline = None
                        if stage == OpportunityStages.STAGE_1 and task_config.get('deadline_days'):
                            deadline = now.date() + timedelta(days=task_config['deadline_days'])
                        
                        OpportunityTask.objects.create(
                            opportunity=opportunity_obj,
                            stage=stage,
                            name=task_config['name'],
                            order=order,
                            deadline=deadline,
                            org=request.profile.org
                        )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create default tasks: {str(e)}", exc_info=True)

            recipients = list(
                opportunity_obj.assigned_to.all().values_list("id", flat=True)
            )

            send_email_to_assigned_user.delay(
                recipients,
                opportunity_obj.id,
            )
            return Response(
                {"error": False, "message": "Opportunity Created Successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class OpportunityDetailView(APIView):
    #authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Opportunity

    def get_object(self, pk):
        return self.model.objects.filter(id=pk).first()

    @extend_schema(
        tags=["Opportunities"],
        parameters=swagger_params1.organization_params,request=OpportunityCreateSwaggerSerializer
    )
    def put(self, request, pk, format=None):
        params = request.data
        opportunity_object = self.get_object(pk=pk)
        if opportunity_object.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            if not (
                (self.request.profile == opportunity_object.created_by)
                or (self.request.profile in opportunity_object.assigned_to.all())
            ):
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = OpportunityCreateSerializer(
            opportunity_object,
            data=params,
            request_obj=request,
            # opportunity=True,
        )

        if serializer.is_valid():
            opportunity_object = serializer.save(closed_on=params.get("due_date"))
            previous_assigned_to_users = list(
                opportunity_object.assigned_to.all().values_list("id", flat=True)
            )
            opportunity_object.contacts.clear()
            if params.get("contacts"):
                contacts_list = params.get("contacts")
                contacts = Contact.objects.filter(id__in=contacts_list, org=request.profile.org)
                opportunity_object.contacts.add(*contacts)

            opportunity_object.tags.clear()
            if params.get("tags"):
                tags = params.get("tags")
                for tag in tags:
                    obj_tag = Tags.objects.filter(slug=tag.lower())
                    if obj_tag.exists():
                        obj_tag = obj_tag[0]
                    else:
                        obj_tag = Tags.objects.create(name=tag)
                    opportunity_object.tags.add(obj_tag)

            if params.get("stage"):
                stage = params.get("stage")
                if stage in ["CLOSED WON", "CLOSED LOST"]:
                    opportunity_object.closed_by = self.request.profile

            opportunity_object.teams.clear()
            if params.get("teams"):
                teams_list = params.get("teams")
                teams = Teams.objects.filter(id__in=teams_list, org=request.profile.org)
                opportunity_object.teams.add(*teams)

            opportunity_object.assigned_to.clear()
            if params.get("assigned_to"):
                assinged_to_list = params.get("assigned_to")
                profiles = Profile.objects.filter(
                    id__in=assinged_to_list, org=request.profile.org, is_active=True
                )
                opportunity_object.assigned_to.add(*profiles)

            if self.request.FILES.get("opportunity_attachment"):
                attachment = Attachments()
                attachment.created_by = self.request.profile.user
                attachment.file_name = self.request.FILES.get(
                    "opportunity_attachment"
                ).name
                attachment.opportunity = opportunity_object
                attachment.attachment = self.request.FILES.get("opportunity_attachment")
                attachment.save()

            assigned_to_list = list(
                opportunity_object.assigned_to.all().values_list("id", flat=True)
            )
            recipients = list(set(assigned_to_list) - set(previous_assigned_to_users))
            send_email_to_assigned_user.delay(
                recipients,
                opportunity_object.id,
            )
            return Response(
                {"error": False, "message": "Opportunity Updated Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        tags=["Opportunities"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        self.object = self.get_object(pk)
        if self.object.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            if self.request.profile != self.object.created_by:
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        self.object.delete()
        return Response(
            {"error": False, "message": "Opportunity Deleted Successfully."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Opportunities"], parameters=swagger_params1.organization_params
    )
    def get(self, request, pk, format=None):
        self.opportunity = self.get_object(pk=pk)
        context = {}
        context["opportunity_obj"] = OpportunitySerializer(self.opportunity).data
        if self.opportunity.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            if not (
                (self.request.profile == self.opportunity.created_by)
                or (self.request.profile in self.opportunity.assigned_to.all())
            ):
                return Response(
                    {
                        "error": True,
                        "errors": "You don't have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        comment_permission = False

        if (
            self.request.profile == self.opportunity.created_by
            or self.request.user.is_superuser
            or self.request.profile.role == "ADMIN"
        ):
            comment_permission = True

        if self.request.user.is_superuser or self.request.profile.role == "ADMIN":
            users_mention = list(
                Profile.objects.filter(is_active=True, org=self.request.profile.org).values(
                    "user__email"
                )
            )
        elif self.request.profile != self.opportunity.created_by:
            if self.opportunity.created_by:
                users_mention = [
                    {"username": self.opportunity.created_by.user.email}
                ]
            else:
                users_mention = []
        else:
            users_mention = []

        context.update(
            {
                "comments": CommentSerializer(
                    self.opportunity.opportunity_comments.all(), many=True
                ).data,
                "attachments": AttachmentsSerializer(
                    self.opportunity.opportunity_attachment.all(), many=True
                ).data,
                "contacts": ContactSerializer(
                    self.opportunity.contacts.all(), many=True
                ).data,
                "users": ProfileSerializer(
                    Profile.objects.filter(
                        is_active=True, org=self.request.profile.org
                    ).order_by("user__email"),
                    many=True,
                ).data,
                "stage": STAGES,
                "lead_source": SOURCES,
                "currency": CURRENCY_CODES,
                "comment_permission": comment_permission,
                "users_mention": users_mention,
            }
        )
        return Response(context)

    @extend_schema(
        tags=["Opportunities"],
        parameters=swagger_params1.organization_params,request=OpportunityDetailEditSwaggerSerializer
    )
    def post(self, request, pk, **kwargs):
        params = request.data
        context = {}
        self.opportunity_obj = Opportunity.objects.get(pk=pk)
        if self.opportunity_obj.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        comment_serializer = CommentSerializer(data=params)
        if self.request.profile.role != "ADMIN" and not self.request.user.is_superuser:
            if not (
                (self.request.profile == self.opportunity_obj.created_by)
                or (self.request.profile in self.opportunity_obj.assigned_to.all())
            ):
                return Response(
                    {
                        "error": True,
                        "errors": "You don't have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        if comment_serializer.is_valid():
            if params.get("comment"):
                comment_serializer.save(
                    opportunity_id=self.opportunity_obj.id,
                    commented_by_id=self.request.profile.id,
                )

            if self.request.FILES.get("opportunity_attachment"):
                attachment = Attachments()
                attachment.created_by = self.request.profile.user
                attachment.file_name = self.request.FILES.get(
                    "opportunity_attachment"
                ).name
                attachment.opportunity = self.opportunity_obj
                attachment.attachment = self.request.FILES.get("opportunity_attachment")
                attachment.save()

        comments = Comment.objects.filter(opportunity=self.opportunity_obj).order_by(
            "-id"
        )
        attachments = Attachments.objects.filter(
            opportunity=self.opportunity_obj
        ).order_by("-id")
        context.update(
            {
                "opportunity_obj": OpportunitySerializer(self.opportunity_obj).data,
                "attachments": AttachmentsSerializer(attachments, many=True).data,
                "comments": CommentSerializer(comments, many=True).data,
            }
        )
        return Response(context)


class OpportunityCommentView(APIView):
    model = Comment
    #authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return self.model.objects.get(pk=pk)

    @extend_schema(
        tags=["Opportunities"],
        parameters=swagger_params1.organization_params,request=OpportunityCommentEditSwaggerSerializer
    )
    def put(self, request, pk, format=None):
        params = request.data
        obj = self.get_object(pk)
        if (
            request.profile.role == "ADMIN"
            or request.user.is_superuser
            or request.profile == obj.commented_by
        ):
            serializer = CommentSerializer(obj, data=params)
            if params.get("comment"):
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {"error": False, "message": "Comment Submitted"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"error": True, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {
                "error": True,
                "errors": "You don't have permission to perform this action.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    @extend_schema(
        tags=["Opportunities"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        self.object = self.get_object(pk)
        if (
            request.profile.role == "ADMIN"
            or request.user.is_superuser
            or request.profile == self.object.commented_by
        ):
            self.object.delete()
            return Response(
                {"error": False, "message": "Comment Deleted Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "error": True,
                "errors": "You do not have permission to perform this action",
            },
            status=status.HTTP_403_FORBIDDEN,
        )


class OpportunityAttachmentView(APIView):
    model = Attachments
    #authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Opportunities"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        self.object = self.model.objects.get(pk=pk)
        if (
            request.profile.role == "ADMIN"
            or request.user.is_superuser
            or request.profile == self.object.created_by
        ):
            self.object.delete()
            return Response(
                {"error": False, "message": "Attachment Deleted Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "error": True,
                "errors": "You don't have permission to perform this action.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )



class OpportunityTaskListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, opportunity_id):
        """Get all tasks for an opportunity"""
        from opportunity.models import OpportunityTask
        from opportunity.serializer import OpportunityTaskSerializer
        
        tasks = OpportunityTask.objects.filter(
            opportunity_id=opportunity_id,
            org=request.profile.org
        ).order_by('stage', 'order', '-created_at')
        
        serializer = OpportunityTaskSerializer(tasks, many=True)
        return Response({
            'error': False,
            'tasks': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, opportunity_id):
        """Create a new task"""
        from opportunity.models import OpportunityTask
        from opportunity.serializer import OpportunityTaskCreateSerializer
        
        opportunity = Opportunity.objects.filter(
            id=opportunity_id,
            org=request.profile.org
        ).first()
        
        if not opportunity:
            return Response({
                'error': True,
                'message': 'Opportunity not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OpportunityTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(
                opportunity=opportunity,
                org=request.profile.org
            )
            return Response({
                'error': False,
                'message': 'Task created successfully',
                'task': OpportunityTaskSerializer(task).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': True,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OpportunityTaskDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, task_id, org):
        from opportunity.models import OpportunityTask
        return OpportunityTask.objects.filter(id=task_id, org=org).first()

    def put(self, request, task_id):
        """Update a task"""
        from opportunity.serializer import OpportunityTaskSerializer
        from opportunity.models import OpportunityTask
        from django.utils import timezone
        from datetime import timedelta
        import logging
        
        logger = logging.getLogger(__name__)
        
        task = self.get_object(task_id, request.profile.org)
        if not task:
            return Response({
                'error': True,
                'message': 'Task not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OpportunityTaskCreateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            updated_task = serializer.save()
            opportunity = updated_task.opportunity
            
            # Check if all tasks in current stage are completed
            stage_tasks = OpportunityTask.objects.filter(
                opportunity=opportunity,
                stage=updated_task.stage
            )
            all_completed = all(t.completed for t in stage_tasks)
            
            logger.info(f"Task {task_id} updated. Stage: {updated_task.stage}, All completed: {all_completed}")
            
            deadlines_updated = False
            if all_completed:
                now = timezone.now()
                
                # Check if there's a next stage
                next_stage = OpportunityStages.NEXT_STAGE.get(updated_task.stage)
                completion_field = OpportunityStages.COMPLETION_FIELD.get(updated_task.stage)
                
                if next_stage and completion_field:
                    
                    # Check if stage hasn't been completed before
                    if not getattr(opportunity, completion_field):
                        logger.info(f"{updated_task.stage} stage completed for opportunity {opportunity.id}. Adding deadlines to {next_stage} tasks...")
                        
                        # Mark stage as completed
                        setattr(opportunity, completion_field, now)
                        opportunity.stage = next_stage
                        opportunity.save()
                        
                        # Add deadlines to next stage tasks using configuration
                        next_stage_tasks = OpportunityTask.objects.filter(
                            opportunity=opportunity,
                            stage=next_stage
                        ).order_by('order')
                        
                        # Get deadline configuration for next stage
                        task_configs = DEFAULT_OPPORTUNITY_TASKS.get(next_stage, [])
                        
                        for idx, task_obj in enumerate(next_stage_tasks):
                            if idx < len(task_configs):
                                deadline_days = task_configs[idx].get('deadline_days')
                                if deadline_days is not None:
                                    task_obj.deadline = now.date() + timedelta(days=deadline_days)
                                    task_obj.save()
                                    logger.info(f"Updated {next_stage} task deadline: {task_obj.name} -> {task_obj.deadline}")
                        
                        deadlines_updated = True
            
            return Response({
                'error': False,
                'message': 'Task updated successfully',
                'task': OpportunityTaskSerializer(updated_task).data,
                'stage_advanced': all_completed,
                'deadlines_updated': deadlines_updated
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': True,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        """Delete a task"""
        task = self.get_object(task_id, request.profile.org)
        if not task:
            return Response({
                'error': True,
                'message': 'Task not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        task.delete()
        return Response({
            'error': False,
            'message': 'Task deleted successfully'
        }, status=status.HTTP_200_OK)


class OpportunityTaskAttachmentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, task_id):
        """Upload attachment to a task"""
        from opportunity.models import OpportunityTask
        
        task = OpportunityTask.objects.filter(
            id=task_id,
            org=request.profile.org
        ).first()
        
        if not task:
            return Response({
                'error': True,
                'message': 'Task not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.FILES.get('attachment'):
            attachment = Attachments()
            attachment.created_by = request.profile.user
            attachment.file_name = request.FILES.get('attachment').name
            attachment.opportunity_task = task
            attachment.attachment = request.FILES.get('attachment')
            attachment.save()
            
            return Response({
                'error': False,
                'message': 'Attachment uploaded successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': True,
            'message': 'No file provided'
        }, status=status.HTTP_400_BAD_REQUEST)



class OpportunityTaskAttachmentDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, attachment_id):
        """Delete an attachment"""
        attachment = Attachments.objects.filter(
            id=attachment_id,
            opportunity_task__org=request.profile.org
        ).first()
        
        if not attachment:
            return Response({
                'error': True,
                'message': 'Attachment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        attachment.delete()
        return Response({
            'error': False,
            'message': 'Attachment deleted successfully'
        }, status=status.HTTP_200_OK)
