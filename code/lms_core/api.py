from ninja import NinjaAPI, UploadedFile, File, Form, Router
from ninja.responses import Response
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from typing import List
from django.http import JsonResponse
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth

from ninja.pagination import paginate, PageNumberPagination
from django.contrib.auth.models import User
from ninja_jwt.authentication import JWTAuth
from .models import Category, Course


# Import semua schema yang diperlukan
from lms_core.schema import (
    CourseSchemaOut, CourseMemberOut, CourseSchemaIn,
    CourseContentMini, CourseContentFull,
    CourseCommentOut, CourseCommentIn,
    UserOut, UserProfileUpdateIn,
    CourseAnnouncementOut, CourseAnnouncementIn, CourseAnnouncementUpdateIn,
    ContentCompletionOut, ContentCompletionIn,
    CourseFeedbackOut, CourseFeedbackIn, CourseFeedbackUpdateIn,
    ContentBookmarkOut, ContentBookmarkIn,
    MessageResponse, ErrorResponse,  CategoryCreateSchema, 
    CategoryUpdateSchema, 
    CategoryResponseSchema,
    CourseCreateSchema,
    CourseUpdateSchema,
    CourseResponseSchema
)

from lms_core.models import (
    Course, CourseMember, CourseContent, Comment,
    UserProfile, CourseAnnouncement, ContentCompletion,
    CourseFeedback, ContentBookmark
)

apiv1 = NinjaAPI()
apiv1.add_router("/auth/", mobile_auth_router)
apiAuth = HttpJwtAuth()
category_router = Router()
course_router = Router()


# ===== PROFIL PENGGUNA ENDPOINTS =====

@apiv1.get("/profile/{user_id}", response=UserOut)
def show_profile(request, user_id: int):
    """
    Menampilkan profil lengkap pengguna berdasarkan ID.
    Tidak memerlukan autentikasi (publik).
    """
    user = get_object_or_404(User, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)
    courses_created = Course.objects.filter(teacher=user)
    course_members = CourseMember.objects.select_related('course_id').filter(user_id=user)
    return {
    'id': user.id,
    'first_name': user.first_name,
    'last_name': user.last_name,
    'email': user.email,
    'username': user.username,
    'profile': {
        'phone': profile.phone,
        'description': profile.description,
        'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
        'created_at': profile.created_at,
        'updated_at': profile.updated_at,
    },
    'courses_created': courses_created,
    'courses_joined': course_members,

}
  

@apiv1.put("/profile", auth=apiAuth, response=MessageResponse) 
def update_profile_no_auth(request, data: UserProfileUpdateIn = Form(...), profile_picture: UploadedFile = File(None)):
    """
    Mengedit profil pengguna - dapat diakses tanpa authentication.
    PERINGATAN: Endpoint ini tidak aman karena tidak ada validasi user!
    
    Penggunaan:
    1. JSON only: Content-Type: application/json
    2. Form data only: Content-Type: multipart/form-data  
    3. JSON + File: Content-Type: multipart/form-data dengan data sebagai form field
    """
    print(f"DEBUG - request.user: {request.user.id}")
    print(f"DEBUG - request.user type: {type(request.user)}")
    

    user_instance = User.objects.get(id=request.user.id)
    
    with transaction.atomic():
        # Update User fields
        if data.first_name is not None:
            user_instance.first_name = data.first_name
        if data.last_name is not None:
            user_instance.last_name = data.last_name
        if data.email is not None:
            user_instance.email = data.email
        user_instance.save()
        
        # Update UserProfile fields
        profile, created = UserProfile.objects.get_or_create(user=user_instance)
        if data.phone is not None:
            profile.phone = data.phone
        if data.description is not None:
            profile.description = data.description
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.save()
    
    return {"message": "Profil berhasil diperbarui"}
# ===== COURSE ANNOUNCEMENTS ENDPOINTS =====

@apiv1.post("/courses/{course_id}/announcements", auth=apiAuth, response=CourseAnnouncementOut)
def create_announcement(request, course_id: int, data: CourseAnnouncementIn):
    """
    Membuat pengumuman baru untuk kursus (hanya pengajar).
    Header: Authorization: Bearer <token>
    """
    user_instance = User.objects.get(id=request.user.id)
    course = get_object_or_404(Course, id=course_id)
    if course.teacher.id != request.user.id :
        raise HttpError(403, f"Hanya pengajar yang dapat membuat pengumuman. ID user: {request.user.username}")
    print(f"User: {request.user}")
    announcement = CourseAnnouncement.objects.create(
        course=course,
        teacher=user_instance,
        title=data.title,
        content=data.content,
        publish_date=data.publish_date,
        is_active=data.is_active
    )
    return announcement
    

@apiv1.get("/courses/{course_id}/announcements", auth=apiAuth, response=List[CourseAnnouncementOut])
def show_announcements(request, course_id: int):
    """
    Menampilkan semua pengumuman untuk kursus tertentu.
    Header: Authorization: Bearer <token>
    """
    course = get_object_or_404(Course, id=course_id)
    is_teacher = course.teacher.id == request.user.id
    is_member = CourseMember.objects.filter(course_id=course.id, user_id=request.user.id).exists()
    if not (is_teacher or is_member):
        raise HttpError(403, "Anda tidak memiliki akses ke kursus ini")
    announcements = CourseAnnouncement.objects.filter(
        course=course,
        is_active=True,
        publish_date__lte=timezone.now()
    ).order_by('-publish_date')
    return announcements

@apiv1.put("/announcements/{announcement_id}", auth=apiAuth, response=CourseAnnouncementOut)
def edit_announcement(request, announcement_id: int, data: CourseAnnouncementUpdateIn):
    """
    Mengedit pengumuman (hanya pengajar).
    Header: Authorization: Bearer <token>
    """
    user_instance = User.objects.get(id=request.user.id)
    announcement = get_object_or_404(CourseAnnouncement, id=announcement_id)
    if announcement.teacher != user_instance:
        raise HttpError(403, "Hanya pengajar yang membuat pengumuman yang dapat mengeditnya")
    if data.title is not None:
        announcement.title = data.title
    if data.content is not None:
        announcement.content = data.content
    if data.publish_date is not None:
        announcement.publish_date = data.publish_date
    if data.is_active is not None:
        announcement.is_active = data.is_active
    announcement.save()
    return announcement

@apiv1.delete("/announcements/{announcement_id}", auth=apiAuth, response=MessageResponse)
def delete_announcement(request, announcement_id: int):
    """
    Menghapus pengumuman (hanya pengajar).
    Header: Authorization: Bearer <token>
    """
    announcement = get_object_or_404(CourseAnnouncement, id=announcement_id)
    if announcement.teacher.id != request.user.id:
        raise HttpError(403, f"Hanya pengajar yang membuat pengumuman yang dapat menghapusnya {announcement.teacher.id}")
    announcement.delete()
    return {"message": "Pengumuman berhasil dihapus"}

# ===== CONTENT COMPLETION TRACKING ENDPOINTS =====

@apiv1.post("/content/completion", auth=apiAuth, response=ContentCompletionOut)
def add_completion_tracking(request, data: ContentCompletionIn):
    """
    Menandai konten sebagai selesai oleh siswa.
    Header: Authorization: Bearer <token>
    """
    content = get_object_or_404(CourseContent, id=data.content_id)
    student_instance = User.objects.get(id=request.user.id)
    is_member = CourseMember.objects.filter(
        course_id=content.course_id, 
        user_id=request.user.id
    ).exists()
    if not is_member:
        raise HttpError(403, "Anda bukan anggota kursus ini")
    completion, created = ContentCompletion.objects.get_or_create(
        student=student_instance,
        content=content
    )
    if not created:
        raise HttpError(400, "Konten sudah ditandai sebagai selesai")
    return completion

@apiv1.get("/courses/{course_id}/completions", auth=apiAuth, response=List[ContentCompletionOut])
def show_completions(request, course_id: int):
    """
    Menampilkan semua penyelesaian siswa untuk kursus tertentu.
    Header: Authorization: Bearer <token>
    """
    course = get_object_or_404(Course, id=course_id)
    student_instance = User.objects.get(id=request.user.id)
    is_member = CourseMember.objects.filter(
        course_id=course, 
        user_id=request.user.id
    ).exists()
    if not is_member:
        raise HttpError(403, "Anda bukan anggota kursus ini")
    completions = ContentCompletion.objects.filter(
        student=student_instance,
        content__course_id=course
    ).select_related('content', 'content__course_id')
    return completions

@apiv1.delete("/completions/{completion_id}", auth=apiAuth, response=MessageResponse)
def delete_completion(request, completion_id: int):
    """
    Menghapus pelacakan penyelesaian oleh siswa.
    Header: Authorization: Bearer <token>
    """
    completion = get_object_or_404(ContentCompletion, id=completion_id)
    student_instance = User.objects.get(id=request.user.id)
    if completion.student != student_instance:
        raise HttpError(403, f"Anda hanya dapat menghapus penyelesaian sendiri {completion.student} {student_instance}")
    completion.delete()
    return {"message": "Pelacakan penyelesaian berhasil dihapus"}

# ===== COURSE FEEDBACK ENDPOINTS =====

@apiv1.post("/feedback", auth=apiAuth, response=CourseFeedbackOut)
def add_feedback(request, data: CourseFeedbackIn):
    """
    Menambahkan umpan balik untuk kursus.
    Header: Authorization: Bearer <token>
    """
    course = get_object_or_404(Course, id=data.course_id)
    user_instance = User.objects.get(id=request.user.id)
    is_member = CourseMember.objects.filter(
        course_id=course, 
        user_id=request.user.id
    ).exists()
    if not is_member:
        raise HttpError(403, "Anda bukan anggota kursus ini")
    feedback, created = CourseFeedback.objects.update_or_create(
        course=course,
        student=user_instance,
        defaults={
            'rating': data.rating,
            'feedback_text': data.feedback_text
        }
    )
    return feedback

@apiv1.get("/courses/{course_id}/feedback", auth=apiAuth, response=List[CourseFeedbackOut])
def show_feedback(request, course_id: int):
    """
    Menampilkan semua umpan balik untuk kursus tertentu.
    Header: Authorization: Bearer <token>
    """
 
    course = get_object_or_404(Course, id=course_id)
    is_teacher = course.teacher.id == request.user.id
    is_member = CourseMember.objects.filter(course_id=course, user_id=request.user.id).exists()
    if not (is_teacher or is_member):
        return HttpError(403, "Anda tidak memiliki akses ke kursus ini")
    feedback_list = CourseFeedback.objects.filter(course=course).select_related('student')
    return feedback_list

@apiv1.put("/feedback/{feedback_id}", auth=apiAuth, response=CourseFeedbackOut)
def edit_feedback(request, feedback_id: int, data: CourseFeedbackUpdateIn):
    """
    Mengedit umpan balik oleh siswa.
    Header: Authorization: Bearer <token>
    """
    feedback = get_object_or_404(CourseFeedback, id=feedback_id)
    student_instance = User.objects.get(id=request.user.id)
    if feedback.student != student_instance:
        raise HttpError(403, "Anda hanya dapat mengedit umpan balik sendiri")
    if data.rating is not None:
        feedback.rating = data.rating
    if data.feedback_text is not None:
        feedback.feedback_text = data.feedback_text
    feedback.save()
    return feedback

@apiv1.delete("/feedback/{feedback_id}", auth=apiAuth, response=MessageResponse)
def delete_feedback(request, feedback_id: int):
    """
    Menghapus umpan balik oleh siswa.
    Header: Authorization: Bearer <token>
    """
    feedback = get_object_or_404(CourseFeedback, id=feedback_id)
    student_instance = User.objects.get(id=request.user.id)
    if feedback.student != student_instance:
        raise HttpError(403, f"Anda hanya dapat menghapus umpan balik sendiri {feedback.student} {student_instance} ")
    feedback.delete()
    return {"message": "Umpan balik berhasil dihapus"}

# ===== CONTENT BOOKMARKING ENDPOINTS =====

@apiv1.post("/bookmark", auth=apiAuth, response=ContentBookmarkOut)
def add_bookmarking(request, data: ContentBookmarkIn):
    """
    Membuat bookmark pada konten oleh siswa.
    Header: Authorization: Bearer <token>
    """
    content = get_object_or_404(CourseContent, id=data.content_id)
    student_instance = User.objects.get(id=request.user.id)
    is_member = CourseMember.objects.filter(
        course_id=content.course_id, 
        user_id=request.user.id
    ).exists()
    if not is_member:
        raise HttpError(403, f"Anda bukan anggota kursus ini {content.course_id} {request.user.id}")
    bookmark, created = ContentBookmark.objects.get_or_create(
        student=student_instance,
        content=content
    )
    if not created:
        raise HttpError(400, "Konten sudah dibookmark")
    return bookmark

@apiv1.get("/bookmarks", auth=apiAuth, response=List[ContentBookmarkOut])
def show_bookmarks(request):
    """
    Menampilkan semua bookmark yang dibuat siswa.
    Header: Authorization: Bearer <token>
    """
    student_instance = User.objects.get(id=request.user.id)
    bookmarks = ContentBookmark.objects.filter(
        student=student_instance
    ).select_related('content', 'content__course_id')
    return bookmarks

@apiv1.delete("/bookmarks/{bookmark_id}", auth=apiAuth, response=MessageResponse)
def delete_bookmark(request, bookmark_id: int):
    """
    Menghapus bookmark oleh siswa.
    Header: Authorization: Bearer <token>
    """
    bookmark = get_object_or_404(ContentBookmark, id=bookmark_id)
    student_instance = User.objects.get(id=request.user.id)
    if bookmark.student != student_instance:
        raise HttpError(403, "Anda hanya dapat menghapus bookmark sendiri")
    bookmark.delete()
    return {"message": "Bookmark berhasil dihapus"}
