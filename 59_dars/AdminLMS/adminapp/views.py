from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import *
from . import services


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _log_action(request, *, action: str, entity: str, entity_id=None, message: str):
    try:
        AuditLog.objects.create(
            user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
            action=action,
            entity=entity,
            entity_id=entity_id,
            message=message[:255],
            ip_address=_client_ip(request),
            user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:255],
        )
    except Exception:
        # logging must never break app flow
        pass

def login_required_decorator(func):
    return login_required(func,login_url='login_page')

@login_required_decorator
def logout_page(request):
    _log_action(request, action="logout", entity="Auth", message="User logged out")
    logout(request)
    return redirect("login_page")


def login_page(request):
    if request.POST:
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(request, password=password, username=username)
        if user is not None:
            login(request, user)
            _log_action(request, action="login", entity="Auth", message="User logged in")
            return redirect("home_page")

    return render(request, 'login.html')

@login_required_decorator
def home_page(request):
    faculties = services.get_faculties()
    kafedras = services.get_kafedra()
    subjects = services.get_subject()
    teachers = services.get_teacher()
    groups = services.get_groups()
    students = services.get_student()
    ctx={
        'counts' : {
            'faculties':len(faculties),
            'kafedras':len(kafedras),
            'subjects':len(subjects),
            'teachers':len(teachers),
            'groups':len(groups),
            'students':len(students)
        }
    }
    return render(request, 'index.html', ctx)

@login_required_decorator
def faculty_create(request):
    model = Faculty()
    form = FacultyForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="create", entity="Faculty", entity_id=saved.id, message=f"Created faculty: {saved.name}")
        return redirect('faculty_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'faculty/form.html',ctx)

@login_required_decorator
def faculty_edit(request,pk):
    model = Faculty.objects.get(pk=pk)
    form = FacultyForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="edit", entity="Faculty", entity_id=saved.id, message=f"Edited faculty: {saved.name}")
        return redirect('faculty_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'faculty/form.html',ctx)

@login_required_decorator
def faculty_delete(request,pk):
    model = Faculty.objects.get(pk=pk)
    name = model.name
    model.delete()
    _log_action(request, action="delete", entity="Faculty", entity_id=pk, message=f"Deleted faculty: {name}")
    return redirect('faculty_list')

@login_required_decorator
def faculty_list(request):
    faculties=services.get_faculties()
    print(faculties)
    ctx={
        "faculties":faculties
    }
    return render(request,'faculty/list.html',ctx)

# KAFEDRA
@login_required_decorator
def kafedra_create(request):
    model = Kafedra()
    form = KafedraForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()

        actions = request.session.get('actions',[])
        actions += [f"You created kafedra: {request.POST.get('name')}"]
        request.session["actions"] = actions

        kafedra_count = request.session.get('kafedra_count', 0)
        kafedra_count +=1
        request.session["kafedra_count"] = kafedra_count

        _log_action(request, action="create", entity="Kafedra", entity_id=saved.id, message=f"Created kafedra: {saved.name}")

        return redirect('kafedra_list')


    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'kafedra/form.html',ctx)

@login_required_decorator
def kafedra_edit(request,pk):
    model = Kafedra.objects.get(pk=pk)
    form = KafedraForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()

        actions = request.session.get('actions',[])
        actions += [f"You edited kafedra: {request.POST.get('name')}"]
        request.session["actions"] = actions
        _log_action(request, action="edit", entity="Kafedra", entity_id=saved.id, message=f"Edited kafedra: {saved.name}")
        return redirect('kafedra_list')

    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'kafedra/form.html',ctx)

@login_required_decorator
def kafedra_delete(request,pk):
    model = Kafedra.objects.get(pk=pk)
    name = model.name
    model.delete()
    _log_action(request, action="delete", entity="Kafedra", entity_id=pk, message=f"Deleted kafedra: {name}")
    return redirect('kafedra_list')

@login_required_decorator
def kafedra_list(request):
    kafedras=services.get_kafedra()
    ctx={
        "kafedras":kafedras
    }
    return render(request,'kafedra/list.html',ctx)

#SUBJECT
@login_required_decorator
def subject_create(request):
    model = Subject()
    form = SubjectForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="create", entity="Subject", entity_id=saved.id, message=f"Created subject: {saved.name}")
        return redirect('subject_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'subject/form.html',ctx)

@login_required_decorator
def subject_edit(request,pk):
    model = Subject.objects.get(pk=pk)
    form = SubjectForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="edit", entity="Subject", entity_id=saved.id, message=f"Edited subject: {saved.name}")
        return redirect('subject_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'subject/form.html',ctx)

@login_required_decorator
def subject_delete(request,pk):
    model = Subject.objects.get(pk=pk)
    name = model.name
    model.delete()
    _log_action(request, action="delete", entity="Subject", entity_id=pk, message=f"Deleted subject: {name}")
    return redirect('subject_list')

@login_required_decorator
def subject_list(request):
    subjects=services.get_subject()
    ctx={
        "subjects":subjects
    }
    return render(request,'subject/list.html',ctx)

#TEACHER
@login_required_decorator
def teacher_create(request):
    model = Teacher()
    form = TeacherForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        actions = request.session.get('actions',[])
        actions += [f"You added teacher: {request.POST.get('first_name')}"]
        request.session["actions"] = actions
        _log_action(request, action="create", entity="Teacher", entity_id=saved.id, message=f"Created teacher: {saved.first_name} {saved.last_name}")

        return redirect('teacher_list')
    ctx = {
        "model":model,
        "form":form,
        "subject_count": Subject.objects.count(),
        "kafedra_count": Kafedra.objects.count(),
    }
    return render(request,'teacher/form.html',ctx)

@login_required_decorator
def teacher_edit(request,pk):
    model = Teacher.objects.get(pk=pk)
    form = TeacherForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="edit", entity="Teacher", entity_id=saved.id, message=f"Edited teacher: {saved.first_name} {saved.last_name}")
        return redirect('teacher_list')
    ctx = {
        "model":model,
        "form":form,
        "subject_count": Subject.objects.count(),
        "kafedra_count": Kafedra.objects.count(),
    }
    return render(request,'teacher/form.html',ctx)

@login_required_decorator
def teacher_delete(request,pk):
    model = Teacher.objects.get(pk=pk)
    full_name = f"{model.first_name} {model.last_name}"
    model.delete()
    _log_action(request, action="delete", entity="Teacher", entity_id=pk, message=f"Deleted teacher: {full_name}")
    return redirect('teacher_list')

@login_required_decorator
def teacher_list(request):
    teachers=services.get_teacher()
    ctx={
        "teachers":teachers
    }
    return render(request,'teacher/list.html',ctx)

#GROUP
@login_required_decorator
def group_create(request):
    model = Group()
    form = GroupForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="create", entity="Group", entity_id=saved.id, message=f"Created group: {saved.name}")
        return redirect('group_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'group/form.html',ctx)

@login_required_decorator
def group_edit(request,pk):
    model = Group.objects.get(pk=pk)
    form = GroupForm(request.POST or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="edit", entity="Group", entity_id=saved.id, message=f"Edited group: {saved.name}")
        return redirect('group_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'group/form.html',ctx)

@login_required_decorator
def group_delete(request,pk):
    model = Group.objects.get(pk=pk)
    name = model.name
    model.delete()
    _log_action(request, action="delete", entity="Group", entity_id=pk, message=f"Deleted group: {name}")
    return redirect('group_list')

@login_required_decorator
def group_list(request):
    groups=services.get_groups()
    ctx={
        "groups":groups
    }
    return render(request,'group/list.html',ctx)

#STUDENT
@login_required_decorator
def student_create(request):
    model = Student()
    form = StudentForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="create", entity="Student", entity_id=saved.id, message=f"Created student: {saved.first_name} {saved.last_name}")
        return redirect('student_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'student/form.html',ctx)

@login_required_decorator
def student_edit(request,pk):
    model = Student.objects.get(pk=pk)
    form = StudentForm(request.POST or None,request.FILES or None, instance=model)
    if request.POST and form.is_valid():
        saved = form.save()
        _log_action(request, action="edit", entity="Student", entity_id=saved.id, message=f"Edited student: {saved.first_name} {saved.last_name}")
        return redirect('student_list')
    ctx = {
        "model":model,
        "form":form
    }
    return render(request,'student/form.html',ctx)

@login_required_decorator
def student_delete(request,pk):
    model = Student.objects.get(pk=pk)
    full_name = f"{model.first_name} {model.last_name}"
    model.delete()
    _log_action(request, action="delete", entity="Student", entity_id=pk, message=f"Deleted student: {full_name}")
    return redirect('student_list')

@login_required_decorator
def student_list(request):
    students=services.get_student()
    ctx={
        "students":students
    }
    return render(request,'student/list.html',ctx)

@login_required_decorator
def profile(request):
    recent_logs = AuditLog.objects.filter(user=request.user)[:10]
    ctx = {
        "recent_logs": recent_logs,
        "session_actions": request.session.get("actions", []),
        "kafedra_count": request.session.get("kafedra_count", 0),
        "stats": {
            "faculties": Faculty.objects.count(),
            "kafedras": Kafedra.objects.count(),
            "subjects": Subject.objects.count(),
            "teachers": Teacher.objects.count(),
            "groups": Group.objects.count(),
            "students": Student.objects.count(),
            "my_actions": AuditLog.objects.filter(user=request.user).count(),
        },
    }
    return render(request,'profile.html', ctx)