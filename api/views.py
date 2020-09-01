from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites import get_current_site
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.shortcuts import HttpResponse, render
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import constants

from . import forms
from .models import (Assignment, Assistant, Comment, Coordinator, File, Grade,
                     GroupRequest, Guide, GuideRequest, Preference, Project,
                     ProjectRequest, Student, Team)
from .serializers import (AssignmentSerializer, AssistantSerializer,
                          CommentSerializer, CoordinatorSerializer,
                          FileSerializer, GradeSerializer,
                          GroupRequestSerializer, GuideSerializer,
                          PreferenceSerializer, ProjectRequestSerializer,
                          ProjectSerializer, StudentSerializer, TeamSerializer)

# * COORDINATOR


@api_view()
def coordinatorStudent(request):
    response = []
    for student in Student.objects.all().order_by('roll_number'):
        student_data = {
            "student_branch": dict(constants.BRANCH)[student.branch],
            "student_email": student.email,
            "student_id": student.id,
            "student_name": student.name,
            "student_roll_number": student.roll_number,
        }
        try:
            project = Project.objects.get(student=student)
            student_data.setdefault("project_id", project.id)
            student_data.setdefault("project_name", project.title)
        except:
            student_data.setdefault("project_id", None)
            student_data.setdefault("project_name", None)
        try:

            team = Team.objects.get(id=student.team.id)
            student_data.setdefault("group_id", team.id)
        except:
            student_data.setdefault("group_id", None)
        try:
            guide = Guide.objects.get(id=team.guide_id)
            student_data.setdefault("guide_id", guide.id)
            student_data.setdefault("guide_name", guide.name)
        except:
            student_data.setdefault("guide_id", None)
            student_data.setdefault("guide_name", None)
        response.append(student_data)
    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorStudentDetail(request, id):
    response = {}
    try:
        student = Student.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    student_data = {
        "student_branch": student.branch,
        "student_email": student.email,
        "student_photo": "/api" + student.photo.url,
        "student_id": student.id,
        "student_name": student.name,
        "student_roll_number": student.roll_number,
    }
    try:
        project = Project.objects.get(student=student)
        student_data.setdefault("project_id", project.id)
        student_data.setdefault("project_name", project.title)
    except:
        student_data.setdefault("project_id", None)
        student_data.setdefault("project_name", None)
    try:
        team = Team.objects.get(id=student.team.id)
        student_data.setdefault("group_id", team.id)
    except:
        student_data.setdefault("group_id", None)
    try:
        guide = Guide.objects.get(id=team.guide_id)
        student_data.setdefault("guide_id", guide.id)
        student_data.setdefault("guide_name", guide.name)
    except:
        student_data.setdefault("guide_id", None)
        student_data.setdefault("guide_name", None)
    response = student_data
    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorGroup(request):
    response = []
    for team in Team.objects.all().order_by('id'):
        team_data = {
            "team_id": team.id,
        }
        project_data = {}
        try:
            project = Project.objects.get(team_id=team.id)
            project_data.setdefault("project_id", project.id)
            project_data.setdefault("project_name", project.title)
            project_data.setdefault("project_type", project.category)
        except:
            project_data.setdefault("project_id", None)
            project_data.setdefault("project_name", None)
            project_data.setdefault("project_type", None)
        team_data.setdefault("project_data", project_data)
        try:
            # ! team without students should not exist
            students = Student.objects.filter(team_id=team.id)
            leader = Student.objects.get(id=team.leader_id)
            students_data_array = []
            for student in students:
                student_data = {}
                student_data.setdefault("student_id", student.id)
                student_data.setdefault("student_name", student.name)
                student_data.setdefault(
                    "student_photo", ("/api" + student.photo.url) or None)
                students_data_array.append(student_data)
            team_data.setdefault("leader_name", leader.name)
            team_data.setdefault("student_data", students_data_array)
        except:
            team_data.setdefault("leader_name", None)
            team_data.setdefault("student_data", None)
        guide_data = {}
        try:
            guide = Guide.objects.get(id=team.guide_id)
            guide_data.setdefault("guide_id", guide.id)
            guide_data.setdefault("guide_photo", ("/api" +
                                                  guide.photo.url) or None)
            guide_data.setdefault("guide_name", guide.name)
        except:
            guide_data.setdefault("guide_id", None)
            guide_data.setdefault("guide_name", None)
            guide_data.setdefault("guide_photo", None)
        team_data.setdefault("guide_data", guide_data)
        response.append(team_data)
    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorGroupDetail(request, id):
    response = {}
    try:
        team = Team.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    team_data = {
        "team_id": team.id,
    }
    project_data = {}
    try:
        project = Project.objects.get(team_id=team.id)
        project_data.setdefault("project_id", project.id)
        project_data.setdefault("project_name", project.title)
        project_data.setdefault("project_type", project.category)
    except:
        project_data.setdefault("project_id", None)
        project_data.setdefault("project_name", None)
        project_data.setdefault("project_type", None)
    team_data.setdefault("project_data", project_data)
    try:
        # ! team without students should not exist
        students = Student.objects.filter(team=team)
        print(students)
        leader = Student.objects.get(id=team.leader.id)
        print(leader)
        students_data_array = []
        for student in students:
            print(student)
            student_data = {}
            student_data.setdefault("student_id", student.id)
            student_data.setdefault("student_name", student.name)
            student_data.setdefault(
                "student_photo", ("/api" + student.photo.url) or "")
            print(student_data)
            students_data_array.append(student_data)
        print("Student data array:\t", students_data_array)
        team_data.setdefault("leader_name", leader.name)
        team_data.setdefault("student_data", students_data_array)
    except:
        team_data.setdefault("leader_name", None)
        team_data.setdefault("student_data", None)
    guide_data = {}
    try:
        guide = Guide.objects.get(id=team.guide.id)
        guide_data.setdefault("guide_id", guide.id)
        guide_data.setdefault("guide_name", guide.name)
        guide_data.setdefault(
            "guide_photo", ("/api" + guide.photo.url) or None)
    except:
        guide_data.setdefault("guide_id", None)
        guide_data.setdefault("guide_name", None)
        guide_data.setdefault("guide_photo", None)
    team_data.setdefault("guide_data", guide_data)
    response = team_data
    print(response)
    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorGuide(request):
    response = []
    for guide in Guide.objects.all():
        guide_data = {
            "guide_branch": dict(constants.BRANCH)[guide.branch],
            "guide_id": guide.id,
            "guide_name": guide.name
        }
        try:
            teams = Team.objects.filter(guide=guide).order_by("id")
            team_data = []
            for team in teams:
                temp_team_data = {
                    "team_id": team.id
                }
                try:
                    project = Project.objects.get(team=team)
                    temp_team_data.setdefault("project_id", project.id)
                    temp_team_data.setdefault("project_title", project.title)
                except:
                    temp_team_data.setdefault("project_id", None)
                    temp_team_data.setdefault("project_title", None)
                finally:
                    team_data.append(temp_team_data)
            guide_data.setdefault("team_data", team_data)
        except:
            guide_data.setdefault("team_data", None)
        response.append(guide_data)

    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorGuideDetail(request, id):
    response = {}
    try:
        guide = Guide.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    preferences = []
    for preference in guide.preferences.all():
        p = Preference.objects.get(id=preference.id)
        preferences.append(
            {"area_of_interest": p.area_of_interest, "thrust_area": p.thrust_area})
    guide_data = {
        "guide_branch": dict(constants.BRANCH)[guide.branch],
        "guide_id": guide.id,
        "guide_name": guide.name,
        "guide_email": guide.email,
        "guide_preferences": preferences,
        "guide_photo": "/api" + guide.photo.url or None,
    }
    try:
        teams = Team.objects.filter(guide=guide)
        team_data = []
        for team in teams:
            temp_team_data = {
                "team_id": team.id
            }
            try:
                project = Project.objects.get(team=team)
                temp_team_data.setdefault("project_id", project.id)
                temp_team_data.setdefault("project_title", project.title)
            except:
                temp_team_data.setdefault("project_id", None)
                temp_team_data.setdefault("project_title", None)
            finally:
                team_data.append(temp_team_data)
        guide_data.setdefault("team_data", team_data)
    except:
        guide_data.setdefault("team_data", None)

    response = guide_data
    print(response)
    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorProject(request):
    # todo: if submitted link should be disabled
    response = []
    for team in Team.objects.all().order_by("id"):
        project_data = {
            "team_id": team.id
        }
        try:
            project = Project.objects.get(team=team)
            project_data.setdefault("project_exists", True)
            project_data.setdefault("project_id", project.id)
            project_data.setdefault("project_title", project.title)
            project_data.setdefault("project_category", project.category)
            project_data.setdefault("project_domain", project.domain)
            project_data.setdefault("project_description", project.description)
            project_data.setdefault(
                "project_explanatory_field", project.explanatory_field or None)
        except:
            project_data.setdefault("project_exists", False)
        try:
            guide = Guide.objects.get(id=team.guide.id)
            project_data.setdefault("guide_name", guide.name)
            project_data.setdefault("guide_id", guide.id)
        except:
            project_data.setdefault("guide_name", None)
            project_data.setdefault("guide_id", None)
        response.append(project_data)
    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorProjectDetail(request, id):
    response = {}
    try:
        project = Project.objects.get(id=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    team = Team.objects.get(id=project.team.id)
    project_data = {
        "team_id": team.id
    }
    try:
        project_data.setdefault("project_exists", True)
        project_data.setdefault("project_id", project.id)
        project_data.setdefault("project_title", project.title)
        project_data.setdefault("project_category", project.category)
        project_data.setdefault("project_domain", project.domain)
        project_data.setdefault("project_description", project.description)
        project_data.setdefault(
            "project_explanatory_field", project.explanatory_field or None)
    except:
        project_data.setdefault("project_exists", False)
    try:
        guide = Guide.objects.get(team=team)
        project_data.setdefault("guide_name", guide.name)
        project_data.setdefault("guide_id", guide.id)
    except:
        project_data.setdefault("guide_name", None)
        project_data.setdefault("guide_id", None)
    response = project_data

    return Response(data=response, status=status.HTTP_200_OK)


@api_view()
def coordinatorAssignmentList(request):
    assignments = Assignment.objects.all()
    response = []
    for assignment in assignments:
        try:
            _assignment = {
                "assignment_id": assignment.id,
                "assignment_title": assignment.title,
                "assignment_weightage": assignment.weightage,
                "assignment_description": assignment.description,
                "assignment_due": assignment.due.strftime("%d/%m/%Y, %H:%M:%S"),
                "assignment_posted": assignment.posted.strftime("%d/%m/%Y, %H:%M:%S")
            }
        except:
            _assignment = {
                "assignment_id": assignment.id,
                "assignment_title": assignment.title,
                "assignment_weightage": assignment.weightage,
                "assignment_description": assignment.description,
                "assignment_due": None,
                "assignment_posted": assignment.posted.strftime("%d/%m/%Y, %H:%M:%S")
            }
        response.append(_assignment)
    return Response(data=response)


@api_view(["POST"])
def coordinatorRemoveAttachments(request):
    l = request.data["delete_list"]
    for id in l:
        try:
            File.objects.get(id=id).delete()
        except:
            continue
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def coordinatorAssignmentDetail(request, id):
    if request.method == "GET":
        try:
            assignment = Assignment.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        response = {}
        # assignment details
        assignment_details = {}
        files = File.objects.filter(assignment=assignment).filter(team=None)
        _files = []
        for file in files:
            _files.append({
                "id": file.id,
                "name": file.file.name.split("/")[-1],
                "url": "/api" + file.file.url,
            })
        try:
            _assignment = {
                "assignment_id": assignment.id,
                "assignment_title": assignment.title,
                "assignment_weightage": assignment.weightage,
                "assignment_description": assignment.description,
                "assignment_due": assignment.due.strftime("%Y-%m-%dT%H:%M"),
                "assignment_posted": assignment.posted.strftime("%Y-%m-%dT%H:%M")
            }
        except:
            _assignment = {
                "assignment_id": assignment.id,
                "assignment_title": assignment.title,
                "assignment_weightage": assignment.weightage,
                "assignment_description": assignment.description,
                "assignment_due": None,
                "assignment_posted": assignment.posted.strftime("%Y-%m-%dT%H:%M")
            }
        assignment_details.setdefault("assignment", _assignment)
        assignment_details.setdefault("files", _files)
        response.setdefault("assignment_details", assignment_details)
        # submission status
        submission_status = []
        for team in Team.objects.all():
            _submission_status = {
                "team_id": team.id
            }
            try:
                grade = Grade.objects.filter(
                    assignment=assignment).get(student=team.leader)
                print(grade.marks_obtained)
                if grade.turned_in:
                    _submission_status.setdefault("status", "Submitted")
                    if grade.marks_obtained != None:
                        _submission_status["status"] = "Graded"
                else:
                    _submission_status.setdefault("status", "Unsubmitted")
            except:
                # ! this condition wont be reached as when assignment is deleted grades associated with that assignments are deleted as well.
                _submission_status.setdefault("status", None)
            submission_status.append(_submission_status)
        response.setdefault("submissionStatus", submission_status)
        return Response(data=response)
    elif request.method == "DELETE":
        try:
            assignment = Assignment.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == "PUT":
        try:
            assignment = Assignment.objects.get(id=id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        print("Due Timestamp:\t", request.data["due"])
        data = {
            "title": request.data["title"],
            "description": request.data["description"],
            "weightage": request.data["weightage"],
            "due": timezone.datetime.fromtimestamp(int(request.data.get('due'))),
            "coordinator": Coordinator.objects.get(id=request.user.id),
            "posted": assignment.posted
        }
        print(data)
        serializer = AssignmentSerializer(assignment, data=data)
        if serializer.is_valid():
            serializer.save()
            count = request.data["attachment_count"]
            filekeylist = ["file["+str(i)+"]" for i in range(int(count))]
            for i in range(int(count)):
                File.objects.create(assignment=assignment, team=None,
                                    submitted_by=Coordinator.objects.get(id=request.user.id).email, file=request.FILES[filekeylist[i]])
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view()
def coordinatorGroupSubmissionDetails(request, assignmentId, teamId):
    response = {}
    team = Team.objects.get(id=teamId)
    assignment = Assignment.objects.get(id=assignmentId)
    weightage = assignment.weightage
    students = Student.objects.filter(team=team)
    student_data = []
    for student in students:
        _student_data = {
            "student_id": student.id,
            "student_roll_number": student.roll_number
        }
        try:
            grade = Grade.objects.filter(student=student).filter(
                assignment=assignment).first()
            _student_data.setdefault(
                "student_marks", grade.marks_obtained)
        except:
            _student_data.setdefault(
                "student_marks", None)
        student_data.append(_student_data)
    leader = Student.objects.get(id=team.leader.id)
    try:
        files = File.objects.filter(assignment_id=assignmentId).filter(
            team=team)
        file_list = []
        for file in files:
            _file = {
                "id": file.id,
                "file_name": file.file.name.split("/")[-1],
                "file_url": "/api" + file.file.url
            }
            file_list.append(_file)
    except:
        pass
    response.setdefault("students_data", student_data)
    response.setdefault("file_list", file_list)
    response.setdefault("weightage", weightage)
    return Response(data=response)


@api_view(['POST'])
def coordinatorCreateAssignment(request):
    # print(request.data, request.POST, request.FILES)
    title = request.data.get('title')
    description = request.data.get('description')
    weightage = int(request.data.get('weightage'))
    posted = timezone.datetime.now()
    due = timezone.datetime.fromtimestamp(int(request.data.get('due')))
    coordinator = Coordinator.objects.get(id=request.user.id)

    data = {
        "title": title,
        "description": description,
        "due": due,
        "posted": posted,
        "weightage": weightage,
        "coordinator": coordinator
    }
    serializer = AssignmentSerializer(data=data)
    if serializer.is_valid():
        assignment = serializer.save()
        count = request.data["attachment_count"]
        filekeylist = ["file["+str(i)+"]" for i in range(int(count))]
        for i in range(int(count)):
            File.objects.create(assignment=assignment, team=None,
                                submitted_by=coordinator.email, file=request.FILES[filekeylist[i]])
        return Response(status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def coordinatorSubmissionStatistics(request):
    response = []
    for team in Team.objects.all():
        _team_data_item = {
            "team_id": team.id
        }
        grade_list = []
        try:
            grades = Grade.objects.filter(student=team.leader)
            for grade in grades:
                submission_status = "Not submitted"
                _t_grade = {}
                if grade.turned_in:
                    submission_status = "Submitted"
                    if grade.marks_obtained != None:
                        submission_status = "Graded"
                _t_grade.setdefault("submission_status", submission_status)
                _t_grade.setdefault(
                    "assignment_name", Assignment.objects.get(id=grade.assignment.id).title)
                grade_list.append(_t_grade)
        except:
            pass
        _team_data_item.setdefault("grades", grade_list)
        response.append(_team_data_item)
    return Response(data=response, status=status.HTTP_200_OK)


@api_view(['GET'])
def coordinatorGradingStatistics(request):
    response = []
    for student in Student.objects.all():
        student_data = {
            "roll_number": student.roll_number
        }
        grade_list = []
        try:
            grades = Grade.objects.filter(student=student)
            for grade in grades:
                _grade = {
                    "assignment_name": Assignment.objects.get(id=grade.assignment.id).title
                }
                submission_status = "Not Submitted"
                if grade.turned_in:
                    submission_status = "Submitted"
                    if grade.marks_obtained != None:
                        submission_status = int(grade.marks_obtained)
                _grade.setdefault("marks", submission_status)
                grade_list.append(_grade)
        except:
            pass
        student_data.setdefault("grade_list", grade_list)
        response.append(student_data)
    return Response(data=response, status=status.HTTP_200_OK)


@api_view(["GET"])
def coordinatorGroupRequest(request):
    response = {}
    # GET
    group_requests = []
    for group_request in GroupRequest.objects.all().order_by("generated"):

        print(group_request)

        _t = {
            "id": group_request.id,
            "action": dict(constants.GROUP_ACTION)[group_request.action],
            "status": dict(constants.STATUS)[group_request.status],
            "new_leader": group_request.new_leader.id if (type(group_request.new_leader) is not type(None)) else None,
            "old_leader": group_request.old_leader.id if (type(group_request.old_leader) is not type(None)) else None,
            "add_student":  group_request.add_student.id if (type(group_request.add_student) is not type(None)) else None,
            "remove_student": group_request.remove_student.id if (type(group_request.remove_student) is not type(None)) else None,
            "team": group_request.team.id,
            "description": group_request.description,
            "generated": group_request.generated.strftime("%d/%m/%Y, %H:%M:%S"),
            "processed": group_request.processed.strftime("%d/%m/%Y, %H:%M:%S"),
        }
        group_requests.append(_t)
    response.setdefault("group_requests", group_requests)
    return Response(data=response)


@api_view(["PUT"])
def coordinatorGroupRequestManage(request, id, what):
    group_request = GroupRequest.objects.get(id=id)
    action = group_request.action
    if action == "Change Leader":
        if what == "A":
            team = Team.objects.get(id=group_request.team.id)
            team.leader = group_request.new_leader
            team.save()
            group_request.status = "A"
            group_request.save()
        else:
            group_request.status = "R"
            group_request.save()
    else:
        if what == "A":
            student = Student.objects.get(id=group_request.remove_student)
            student.team = None
            student.save()
            group_request.status = "A"
            group_request.save()
        else:
            group_request.status = "R"
            group_request.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def coordinatorProjectRequest(request):
    res = {}
    project_requests = ProjectRequest.objects.all().order_by("created")
    project_req_list = []
    for project_request in project_requests:
        _t = {
            "project": project_request.project.id,
            # "description": project_request.description,
            "status": project_request.status,
            "id": project_request.id,
            "created": project_request.created.strftime("%d/%m/%Y, %H:%M:%S"),
            "last_modified": project_request.last_modified.strftime("%d/%m/%Y, %H:%M:%S"),
        }
        project_req_list.append(_t)
    res.setdefault("project_requests", project_req_list)
    return Response(data=res, status=status.HTTP_200_OK)


@api_view(["GET", "PUT"])
def coordinatorProjectRequestManage(request, id, what):
    project_request = ProjectRequest.objects.get(id=id)
    if what == "A":
        project_request.status = "A"
        project_request.save()
    if what == "R":
        project = Project.objects.get(id=project_request.project.id)
        project.delete()
        project_request.delete()
        # student notify?

    return Response(status=status.HTTP_204_NO_CONTENT)
# * GUIDE


@api_view()
def guideDashboard(request):
    response = {}
    _user = Guide.objects.get(id=request.user.id)
    group_info = []
    for team in Team.objects.filter(guide=_user):
        member_count = len(Student.objects.filter(team=team))
        _t = {
            "id": team.id,
            "leader_name": team.leader.name,
            "member_count": member_count,
        }
        try:
            project = Project.objects.get(team=team)
            _t.setdefault("domain", project.domain)
            group_info.append(_t)
        except:
            _t.setdefault("domain", None)
            group_info.append(_t)
    response.setdefault("group_info", group_info)
    return Response(data=response)


@api_view()
def guideAssignmentDetails(request, pk, groupId):
    guide = Guide.objects.get(id=request.user.id)
    response = {}
    studentList = []
    for student in Student.objects.filter(team_id=groupId):
        studentData = {
            "student_roll_number": student.roll_number
        }
        try:
            grade = Grade.objects.get(
                student=student, assignment=Assignment.objects.get(pk=pk))
            studentData.setdefault("turned_in", grade.turned_in)
            studentData.setdefault("grade", grade.marks_obtained)
        except:
            studentData.setdefault("turned_in", None)
            studentData.setdefault("grade", None)
        studentList.append(studentData)
    assignment = Assignment.objects.get(pk=pk)
    print(assignment)
    assignmentDetails = {
        "title": assignment.title,
        "description": assignment.description,
        "weightage": assignment.weightage,
        "due": assignment.due.strftime("%d/%m/%Y, %H:%M:%S"),
        "posted": assignment.posted.strftime("%d/%m/%Y, %H:%M:%S")
    }
    fileAttachements = File.objects.filter(team=None, assignment=assignment)
    _attachments = []
    for file in fileAttachements:
        _file = {
            "id": file.id,
            "file_name": file.file.name.split("/")[-1],
            "file_url": '/api'+file.file.url
        }
        _attachments.append(_file)
    assignmentDetails.setdefault("attachments", _attachments)
    teamSubmissions = []
    teamFileUploads = File.objects.filter(team_id=groupId)
    for file in teamFileUploads:
        _file = {
            "id": file.id,
            "file_name": file.file.name.split("/")[-1],
            "file_url": '/api'+file.file.url
        }
        teamSubmissions.append(_file)
    response.setdefault("student_list", studentList)
    response.setdefault("assignment_details", assignmentDetails)
    response.setdefault("team_submissions", teamSubmissions)
    print(response)
    return Response(data=response)


@api_view(["PUT"])
def guideAssignGrades(request):
    print(request.data)
    guide = Guide.objects.get(id=request.user.id)
    for roll, grade in request.data.get("grade").items():
        r = int(roll)
        marks = int(grade)
        as_id = int(request.data.get("id"))

        a = Assignment.objects.get(id=as_id)
        s = Student.objects.get(roll_number=r)
        g = Grade.objects.get(student=s, assignment=a)

        print(g)
        if marks == None:
            g.marks_obtained = None
            g.guide = guide
            g.save()
        if (a.weightage >= marks) and (marks >= 0):
            g.marks_obtained = marks
            g.guide = guide
            g.save()
            # print(_g.marks_obtained)
        else:
            return Response(data="Marks out of range", status=status.HTTP_400_BAD_REQUEST)
    return Response()
    # guide = Guide.objects.get(id=request.user.id)
    # student_grade = request.data.get("student_grade")
    # # print(request.data, type(request.data))
    # for i in student_grade:
    #     _g = Grade.objects.filter(student=i.get("student_id")).filter(
    #         assignment=request.data.get("assignment_id"))[0]
    #     if (_g.assignment.weightage >= i.get("marks_obtained")) and (i.get("marks_obtained") >= 0):
    #         _g.marks_obtained = i.get("marks_obtained")
    #         _g.save()
    #         # print(_g.marks_obtained)
    #     else:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    # return Response()


@api_view(['GET', 'PUT', 'DELETE'])
def guideAssignmentList(request, groupId):
    guide = Guide.objects.get(id=request.user.id)
    team = Team.objects.get(id=groupId)
    grades = Grade.objects.filter(student=team.leader)
    response = []
    for grade in grades:
        _assignment = Assignment.objects.get(grade=grade)
        try:
            _t = {
                "assignment_id": _assignment.id,
                "assignment_title": _assignment.title,
                "assignment_due": _assignment.due.strftime("%d/%m/%Y, %H:%M:%S"),
                "assignment_posted": _assignment.posted.strftime("%d/%m/%Y, %H:%M:%S"),
                "assignment_weightage": _assignment.weightage,
            }
        except:
            _t = {
                "assignment_id": _assignment.id,
                "assignment_title": _assignment.title,
                "assignment_due": None,
                "assignment_posted": _assignment.posted.strftime("%d/%m/%Y, %H:%M:%S"),
                "assignment_weightage": _assignment.weightage,
            }
        if grade.turned_in:
            _t.setdefault("grading_status", "Submitted")
            if grade.marks_obtained != None:
                _t.setdefault("grading_status", "Graded")
        else:
            _t.setdefault("grading_status", "Not Submitted")
        _t.setdefault("team_id", team.id)
        response.append(_t)
    return Response(data=response)


@api_view()
def guideRequest(request):
    guide = Guide.objects.get(id=request.user.id)
    print(guide)
    requests = GuideRequest.objects.filter(
        guide=guide, status="P").order_by("timestamp_requested")
    print(request)
    guide_req_list = []
    for guide_request in requests:
        _g = {
            "team": guide_request.team.id,
            "status": guide_request.status,
            "id": guide_request.id,
            "timestamp_requested": guide_request.timestamp_requested.strftime("%d/%m/%Y, %H:%M:%S"),
        }
        print(_g)
        guide_req_list.append(_g)
    print(guide_req_list)
    return Response(data=guide_req_list, status=status.HTTP_200_OK)


@api_view()
def guideHeader(request):
    guide = Guide.objects.get(id=request.user.id)

    alloted_teams_count = Team.objects.filter(guide=guide).count()

    return Response(data=alloted_teams_count)


@api_view(["POST"])
def acceptRequest(request):
    guide = Guide.objects.get(id=request.user.id)
    team = Team.objects.get(id=request.data.get("team_id"))

    alloted_teams_count = Team.objects.filter(guide=guide).count()

    if alloted_teams_count < 2:
        gr = GuideRequest.objects.get(status="P", guide=guide, team=team)
        gr.status = "A"
        gr.save()
        team.guide = guide
        team.save()
        return Response(data="Group request accepted")
    else:
        gr = GuideRequest.objects.get(status="P", guide=guide, team=team)
        gr.status = "R"
        gr.save()
        return Response(data="Cannot assign more than 2 groups", status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def rejectRequest(request):
    guide = Guide.objects.get(id=request.user.id)
    team = Team.objects.get(id=request.data.get("team_id"))

    gr = GuideRequest.objects.get(status="P", guide=guide, team=team)
    gr.status = "R"
    gr.save()

    return Response(data="Request rejected")


@api_view(['PUT'])
def guideDetailsForm(request):
    guide = Guide.objects.get(id=request.user.id)
    data = request.data
    # if len(data["preferences"]) > 4:
    #    return Response(status=status.HTTP_400_BAD_REQUEST)
    for preference in data["preferences"]:
        if not preference["area_of_interest"] in [i[1] for i in constants.DOMAIN]:
            return Response(data="Invalid Input", status=status.HTTP_400_BAD_REQUEST)
        if not preference["thrust_area"] in [i[1] for i in constants.THRUST_AREA]:
            return Response(data="Invalid Input 1", status=status.HTTP_400_BAD_REQUEST)
    guide.initials = data["initials"]
    guide.preferences.clear()
    guide.save()
    for preference in data["preferences"]:
        _p = Preference.objects.filter(area_of_interest=preference["area_of_interest"]).filter(
            thrust_area=preference["thrust_area"]).first()
        if _p == None:
            _p = Preference.objects.create(
                area_of_interest=preference["area_of_interest"], thrust_area=preference["thrust_area"])
        guide.preferences.add(_p)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view()
def guidePersonal(request):
    guide = Guide.objects.get(id=request.user.id)
    guide_data = {
        "branch": guide.branch,
        "id": guide.id,
        "initials": guide.initials,
        "name": guide.name,
        "email": guide.email,
    }
    preferences = []
    if(guide.preferences.all()):
        for preference in guide.preferences.all():
            p = Preference.objects.get(id=preference.id)
            preferences.append(
                {"area_of_interest": p.area_of_interest, "thrust_area": p.thrust_area})
    else:
        preferences = None
    try:
        teams = Team.objects.filter(guide=guide)
        team_data = []
        for team in teams:
            temp_team_data = {
                "team_id": team.id
            }
            team_data.append(temp_team_data)
        guide_data.setdefault("teams", team_data)
    except:
        guide_data.setdefault("teams", None)
    guide_data.setdefault("preferences", preferences)
    return Response(data=guide_data)


@api_view(['GET'])
def guideGroup(request, groupId):
    guide = Guide.objects.get(id=request.user.id)
    team = Team.objects.get(id=groupId)
    leader = Student.objects.get(id=team.leader.id)
    students = Student.objects.filter(team=team.id)
    response = {
        "team_id": team.id,
        "leader": leader.name
    }
    member_list = []
    for student in students:
        _s = {
            "student_name": student.name,
            "student_email": student.email,
            "student_roll_number": student.roll_number,
            "student_branch": student.branch
        }
        member_list.append(_s)
    project = Project.objects.filter(team=team).first()
    if project != None:
        project_details = {
            "project_id": project.id,
            "project_title": project.title,
            "project_description": project.description,
            "project_domain": dict(constants.DOMAIN)[project.domain],
            "project_category": dict(constants.CATEGORY)[project.category],
            "project_explanatory_field": project.explanatory_field,
        }
    else:
        project_details = {}
    response.setdefault("students", member_list)
    response.setdefault("project", project_details)
    return Response(data=response)

# * STUDENT


@api_view()
def studentPersonal(request):
    student = Student.objects.get(id=request.user.id)
    response = {
        "name": student.name,
        "roll_number": student.roll_number,
        "branch": dict(constants.BRANCH)[student.branch],
        "email": student.email,
    }
    return Response(data=response)


@api_view()
def amILeader(request):
    student = Student.objects.get(id=request.user.id)
    try:
        if student.team.leader == student:
            return Response(data=True)
        else:
            return Response(data=False)
    except:
        return Response(data=False)


@api_view()
def groupRegistered(request):
    student = Student.objects.get(id=request.user.id)
    if student.team:
        return Response(data=True)
    else:
        return Response(data=False, status=status.HTTP_404_NOT_FOUND)


@api_view()
def myRollNumber(request):
    student = Student.objects.get(id=request.user.id)
    return Response(data=student.roll_number)


@api_view(["POST"])
def createTeam(request):
    roll1 = Student.objects.get(id=request.user.id).roll_number
    roll2 = request.data["roll2"]
    roll3 = request.data["roll3"]
    roll4 = request.data["roll4"]

    roll_list = [roll1, roll2, roll3, roll4]
    try:
        roll_list = [int(roll) for roll in roll_list if roll != ""]
    except:
        return Response(data="Roll number is badly formatted", status=status.HTTP_400_BAD_REQUEST)

    student_list = []
    for roll_number in set(roll_list):
        try:
            student = Student.objects.get(roll_number=roll_number)
        except:
            return Response(data=f"{roll_number} has not signed up", status=status.HTTP_400_BAD_REQUEST)
        if student.team != None:
            del student_list
            return Response(data=f"{roll_number} is already in a group", status=status.HTTP_400_BAD_REQUEST)
        else:
            student_list.append(student)

    leader = Student.objects.get(id=request.user.id)
    team = Team.objects.create(leader=leader)
    for student in student_list:
        student.team = team
        student.save()

    return Response(status=status.HTTP_201_CREATED)


@api_view()
def studentAssignments(request):
    student = Student.objects.get(id=request.user.id)
    grades = Grade.objects.filter(student=student)
    # print(grades)
    response = []
    for grade in grades:
        assignment = Assignment.objects.get(id=grade.assignment.id)
        submission_status = None
        if grade.turned_in:
            submission_status = "submitted"
            if grade.marks_obtained != None:
                submission_status = "graded"
        else:
            submission_status = "not-submitted"
        try:
            due = assignment.due.strftime("%d/%m/%Y, %H:%M:%S")
        except:
            due = None
        t = {
            "id": assignment.id,
            "title": assignment.title,
            "due": due,
            "weightage": assignment.weightage,
            "posted": assignment.posted.strftime("%d/%m/%Y, %H:%M:%S"),
            "status": submission_status
        }
        response.append(t)
    # print(response)
    return Response(data=response)


@api_view()
def groupData(request):
    student = Student.objects.get(id=request.user.id)
    team = Team.objects.get(id=student.team.id)
    leader = team.leader

    students = Student.objects.filter(team=team)
    members = []
    for student in students:
        t = {
            "id": student.id,
            "name": student.name,
            "roll_number": student.roll_number,
            "branch": dict(constants.BRANCH)[student.branch],
            "email": student.email,
        }
        members.append(t)

    response = {
        "group_id": team.id,
        "leader_name": leader.name,
        "members": members
    }
    return Response(data=response)


@api_view()
def assignment(request, id):
    try:
        assignment = Assignment.objects.get(id=id)
        files = File.objects.filter(assignment=assignment, team=None)
        attachments = []
        for attachment in files:
            t = {
                "id": attachment.id,
                "name": attachment.file.name.split("/")[-1],
                "url": ("/api" + attachment.file.url)
            }
            attachments.append(t)
        try:
            due = assignment.due.strftime("%d/%m/%Y, %H:%M:%S")
        except:
            due = None
        response = {
            "title": assignment.title,
            "description": assignment.description,
            "due": due,
            "posted": assignment.posted.strftime("%d/%m/%Y, %H:%M:%S"),
            "weightage": assignment.weightage,
            "attachments": attachments
        }
        return Response(data=response)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def assignmentSubmit(request, id):
    user = request.user
    team = Student.objects.get(id=user.id).team
    assignment = Assignment.objects.get(id=id)
    for file in request.FILES.values():
        try:
            form = File.objects.create(
                submitted_by=user.email, assignment=assignment, team=team, file=file)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    for student in Student.objects.filter(team=team):
        grade = Grade.objects.get(assignment=Assignment.objects.get(
            id=id), student=student)
        grade.turned_in = True
        grade.save()
    return Response(status=status.HTTP_201_CREATED)


@api_view()
def studentAssignmentDetails(request, id):
    student = Student.objects.get(id=request.user.id)
    assignment = Assignment.objects.get(id=id)
    grade = Grade.objects.get(assignment=assignment, student=student)
    grade = GradeSerializer(instance=grade)
    files = File.objects.filter(team=student.team)
    response = {
        "grade": grade.data,
        "my_submissions": [{"id": _file.id,
                            "name": _file.file.name.split("/")[-1],
                            "url": ("/api" + _file.file.url)} for _file in files]
    }
    return Response(data=response)


@api_view(["DELETE"])
def studentUnsubmitAssignment(request, id):
    student = Student.objects.get(id=request.user.id)
    assignment = Assignment.objects.get(id=id)
    team_members = Student.objects.filter(team=student.team)
    for member in team_members:
        grade = Grade.objects.get(assignment=assignment, student=member)
        grade.turned_in = False
        grade.marks_obtained = None
        grade.guide = None
        grade.save()
    files = File.objects.filter(assignment=assignment, team=student.team)
    for file in files:
        file.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def addStudent(request):
    try:
        student_to_add = Student.objects.get(
            roll_number=int(request.data["roll"]))
        if student_to_add.team == None:
            me = Student.objects.get(id=request.user.id)
            if len(Student.objects.filter(team=me.team)) <= 3:
                student_to_add.team = me.team
                student_to_add.save()
                return Response(data="Added student to the group", status=status.HTTP_201_CREATED)
            else:
                return Response(data="Maximum four students can be in a group", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data="Student is already in some group", status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response(data="Student has not registered", status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def removeStudent(request):
    try:
        student_to_remove = Student.objects.get(
            roll_number=int(request.data["roll"]))
        leader = Student.objects.get(id=request.user.id)
        if student_to_remove.team == leader.team:
            if leader == student_to_remove:
                return Response("Transfer leadership to someone else in the team before removing yourself", status=status.HTTP_400_BAD_REQUEST)
            if len(GroupRequest.objects.filter(action="Removal", status="P", remove_student=student_to_remove, team=Student.objects.get(id=request.user.id).team)) > 0:
                return Response(data="Removal request for the student has already been sent", status=status.HTTP_400_BAD_REQUEST)
            try:
                GroupRequest.objects.create(status="P", action="Removal", remove_student=student_to_remove,
                                            description=request.data["reason"], team=Student.objects.get(id=request.user.id).team)
                return Response(data="Removal Request has been sent", status=status.HTTP_201_CREATED)
            except:
                return Response(data="Error sending request", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data="Student not in the group", status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response(data="Student not in the group or has not registered", status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def makeLeader(request):
    student = Student.objects.get(id=request.user.id)
    if len(GroupRequest.objects.filter(action="Change Leader", team=student.team)) > 0:
        return Response(data="Previous change leader request pending", status=status.HTTP_400_BAD_REQUEST)
    if student.team.leader == student:
        new_leader = request.data["new_leader"]
        try:
            GroupRequest.objects.create(action="Change Leader", new_leader=Student.objects.get(id=new_leader),
                                        old_leader=student, status="P", team=student.team)
            return Response(data="Request sent", status=status.HTTP_201_CREATED)
        except:
            return Response(data="Error sending request", status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data="Insufficient permissions", status=status.HTTP_400_BAD_REQUEST)


@api_view()
def searchGuide(request, q):
    response = []
    guides = Guide.objects.filter(Q(name__icontains=q) | Q(email__icontains=q))
    for guide in guides:
        team_count = Team.objects.filter(guide=guide).count()
        if team_count < 2:
            response.append({
                "name": guide.name,
                "id": guide.id,
                "email": guide.email,
                "branch": dict(constants.BRANCH)[guide.branch]
            })
    return Response(data=response)


@api_view()
def guideAssigned(request):
    student = Student.objects.get(id=request.user.id)
    # print(student.team.guide)
    if student.team.guide:
        guide = Guide.objects.get(id=student.team.guide_id)
        response = {
            "approved": True,
            "name": guide.name,
            "email": guide.email,
            "branch": dict(constants.BRANCH)[guide.branch]
        }
        return Response(data=response)
    else:
        gr = GuideRequest.objects.filter(team=student.team, status="P")
        if len(gr) > 0:
            # print(dir(gr.first()))
            guide = Guide.objects.get(id=gr.first().guide_id)
            response = {
                "approved": False,
                "name": guide.name,
                "email": guide.email,
                "branch": dict(constants.BRANCH)[guide.branch],
                "ref": gr.first().id
            }
            return Response(data=response)
    return Response(data=False)


@api_view(["POST"])
def cancelRequest(request):
    try:
        GuideRequest.objects.get(id=request.data["id"]).delete()
        return Response(data="Request cancelled", status=status.HTTP_200_OK)
    except:
        return Response(data="Error cancelling request", status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def requestGuide(request):
    leader = Student.objects.get(id=request.user.id)

    requested_guide = Guide.objects.get(id=request.data["id"])
    if len(GuideRequest.objects.filter(team=leader.team, status="P")) > 0:
        return Response(data="Earlier request pending", status=status.HTTP_400_BAD_REQUEST)
    try:
        GuideRequest.objects.create(
            team=leader.team, guide=requested_guide, status="P")
        return Response(data="Request sent", status=status.HTTP_201_CREATED)
    except:
        return Response(data="Error sending request", status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def createProject(request):
    student = Student.objects.get(id=request.user.id)
    team = Team.objects.get(id=student.team.id)
    data = {
        "title": request.data["title"],
        "description": request.data["description"],
        "explanatory_field": request.data["interDisciplinaryReason"],
        "domain": dict([(t[1], t[0]) for t in constants.DOMAIN])[request.data["domain"]],
        "category": dict([(t[1], t[0]) for t in constants.CATEGORY])[request.data["type"]],
        "team": team.id
    }
    s = ProjectSerializer(data=data)
    print(data)
    if s.is_valid():
        ins = s.save()
        prs = ProjectRequestSerializer(data={"status": "P", "project": ins.id})
        if prs.is_valid():
            prs.save()
            for student in Student.objects.filter(team=team):
                student.project = ins
                student.save()
            return Response(data="Project request sent", status=status.HTTP_201_CREATED)
        else:
            ins.delete()
            return Response(prs.errors, status=status.HTTP_400_BAD_REQUEST)
            # return Response(data="Error sending project request", status=status.HTTP_400_BAD_REQUEST)

    # return Response(data="Error creating project", status=status.HTTP_400_BAD_REQUEST)
    return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def getProject(request):
    student = Student.objects.get(id=request.user.id)
    try:
        project = Project.objects.get(id=student.project.id)
        pr = ProjectRequest.objects.get(project=project)
        if pr.status == "A":
            response = {
                "applied": True,
                "approved": True,
                "title": project.title,
                "description": project.description,
                "domain": dict(constants.DOMAIN)[project.domain],
                "type": dict(constants.CATEGORY)[project.category],
                "interDisciplinaryReason": project.explanatory_field
            }
            return Response(data=response, status=status.HTTP_200_OK)
        if pr.status == "P":
            response = {
                "applied": True,
                "approved": False,
                "title": project.title,
                "description": project.description,
                "domain": dict(constants.DOMAIN)[project.domain],
                "type": dict(constants.CATEGORY)[project.category],
                "interDisciplinaryReason": project.explanatory_field
            }
            return Response(data=response, status=status.HTTP_200_OK)
    except:
        return Response(data={"applied": False, "approved": False, "message": "Not registered any project"}, status=status.HTTP_404_NOT_FOUND)


# * ASSISTANT
# * AUTHENTICATION AND MISCELLANEOUS
""" change profile picture and password """


@ api_view()
def whoAmI(request):
    try:
        userType = request.user.groups.all()[0].name.lower()
        return Response(data=userType, status=status.HTTP_200_OK)
    except:
        return Response(data=None, status=status.HTTP_200_OK)


@ api_view()
def signOut(request):
    logout(request)
    return Response(status=status.HTTP_200_OK)


@ api_view(['POST'])
@ permission_classes([permissions.AllowAny])
def signIn(request):
    if request.method == 'POST':
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse()
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@ api_view(['POST'])
@ permission_classes([permissions.AllowAny])
def signUp(request):
    if request.method == 'POST':
        email = request.data.get("email")
        password = request.data.get("password")
        name = request.data.get("name")
        roll_number = request.data.get("rollNumber")
        branch = request.data.get("branch")
        if branch == "Information Technology":
            branch = "IT"
        elif branch == "Computer Science":
            branch = "CS"
        elif branch == "Mechanical":
            branch = "MECH"
        elif branch == "Electronics":
            branch = "ETRX"
        elif branch == "Electronics and Telecommunication":
            branch = "EXTC"
        data = {
            "name": " ".join(name.split()).title(),
            "email": email,
            "password": password,
            "branch": branch,
            "roll_number": roll_number,
            # "photo": None,
            "is_staff": False,
            "is_active": False
        }
        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            student = serializer.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('email_template.html', {
                'user': student,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(student.pk)),
                'token': account_activation_token.make_token(student),
            })
            to_email = email
            send_mail(mail_subject, message, 'youremail', [to_email])
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        student = Student.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Student.DoesNotExist):
        student = None
    if student is not None and account_activation_token.check_token(student, token):
        student.is_active = True
        student.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


@api_view(['POST'])
def guideSignUp(request):
    if request.method == 'POST':
        if request.user.has_perm('api.add_guide'):
            email = request.data.get("email")
            password = request.data.get("password")
            name = request.data.get("name")
            initials = request.data.get("initials")
            branch = request.data.get("branch")
            if branch == "Information Technology":
                branch = "IT"
            elif branch == "Computer Science":
                branch = "CS"
            elif branch == "Mechanical":
                branch = "MECH"
            elif branch == "Electronics":
                branch = "ETRX"
            elif branch == "Electronics and Telecommunication":
                branch = "EXTC"
            print(request.data)
            data = {
                "name": " ".join(name.split()).title(),
                "email": email,
                "password": password,
                "branch": branch,
                "initials": initials,
                # "photo": None,
                "is_staff": False,
                "is_active": True
            }

            serializer = GuideSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["POST"])
def changePassword(request):
    user = request.user
    user.set_password(request.data.get("newPassword"))
    user.save()
    login(request, user)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def changePhoto(request):
    user = request.user

    form = forms.StudentForm(request.POST, request.FILES)
    if form.is_valid():
        f = form.save(commit=False)
        user.photo = f.photo
        user.save()
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view()
def getImage(request):
    try:
        url = ("/api" + request.user.photo.url)
        return Response(data=url, status=status.HTTP_200_OK)
    except:
        url = None
        return Response(data=url, status=status.HTTP_404_NOT_FOUND)
