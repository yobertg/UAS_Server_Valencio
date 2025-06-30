from ninja import Schema, ModelSchema
from typing import List, Optional, ForwardRef
from datetime import datetime

from django.contrib.auth.models import User
from .models import (
    UserProfile, CourseAnnouncement, ContentCompletion, 
    CourseFeedback, ContentBookmark, Course, CourseContent, CourseMember
)
from pydantic import BaseModel, Field

# Forward references untuk mengatasi circular imports
CourseSchemaOutRef = ForwardRef('CourseSchemaOut')
CourseMemberOutRef = ForwardRef('CourseMemberOut')

class CourseOut(Schema):
    id: int
    name: str
    description: Optional[str] = None

class CourseMemberOut(Schema):
    course_id: int
    roles: Optional[str] = None  #

# Basic User Schema
class UserBasic(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    username: str

# User Profile Schemas
class UserProfileOut(ModelSchema):
    class Meta:
        model = UserProfile
        fields = ['phone', 'description', 'profile_picture', 'created_at', 'updated_at']

class UserProfileUpdateIn(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None

# Course Schemas
class CourseSchemaOut(Schema):
    id: int
    name: str
    description: str
    price: int
    image: Optional[str] = None
    teacher: UserBasic
    created_at: datetime
    updated_at: datetime

class CourseSchemaIn(Schema):
    name: str
    description: str
    price: int

# Course Member Schema
class CourseMemberOut(Schema):
    id: int 
    course_id: CourseSchemaOut
    user_id: UserBasic
    roles: str
    created_at: datetime
    updated_at: datetime

# Extended User Schema dengan relasi
class UserOut(ModelSchema):
    profile: Optional[UserProfileOut] = None
    courses_created: List[CourseOut]
    courses_joined: List[CourseMemberOut]
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username']

# Course Content Schemas
class CourseContentMini(Schema):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

class CourseContentFull(Schema):
    id: int
    name: str
    description: str
    video_url: Optional[str] = None
    file_attachment: Optional[str] = None
    course_id: CourseSchemaOut
    created_at: datetime
    updated_at: datetime

class CourseContentIn(Schema):
    name: str
    description: str
    video_url: Optional[str] = None
    parent_id: Optional[int] = None

# Comment Schemas
class CourseCommentOut(Schema):
    id: int
    content_id: CourseContentMini
    member_id: CourseMemberOut
    comment: str
    created_at: datetime
    updated_at: datetime

class CourseCommentIn(Schema):
    comment: str

# Course Announcement Schemas
class CourseAnnouncementOut(ModelSchema):
    teacher_name: str
    course_name: str
    
    class Meta:
        model = CourseAnnouncement
        fields = ['id', 'title', 'content', 'publish_date', 'is_active', 'created_at', 'updated_at']

    @staticmethod
    def resolve_teacher_name(obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}".strip()
    
    @staticmethod
    def resolve_course_name(obj):
        return obj.course.name

class CourseAnnouncementIn(Schema):
    title: str
    content: str
    publish_date: datetime
    is_active: bool = True

class CourseAnnouncementUpdateIn(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    publish_date: Optional[datetime] = None
    is_active: Optional[bool] = None

# Content Completion Schemas
class ContentCompletionOut(ModelSchema):
    content_name: str
    course_name: str
    
    class Meta:
        model = ContentCompletion
        fields = ['id', 'completed_at']

    @staticmethod
    def resolve_content_name(obj):
        return obj.content.name
    
    @staticmethod
    def resolve_course_name(obj):
        return obj.content.course_id.name

class ContentCompletionIn(Schema):
    content_id: int

# Course Feedback Schemas
class CourseFeedbackOut(ModelSchema):
    student_name: str
    course_name: str
    
    class Meta:
        model = CourseFeedback
        fields = ['id', 'rating', 'feedback_text', 'created_at', 'updated_at']

    @staticmethod
    def resolve_student_name(obj):
        return f"{obj.student.first_name} {obj.student.last_name}".strip()
    
    @staticmethod
    def resolve_course_name(obj):
        return obj.course.name

class CourseFeedbackIn(Schema):
    course_id: int
    rating: int
    feedback_text: str

class CourseFeedbackUpdateIn(Schema):
    rating: Optional[int] = None
    feedback_text: Optional[str] = None

# Content Bookmark Schemas
class ContentBookmarkOut(ModelSchema):
    content_name: str
    course_name: str
    content_description: str
    
    class Meta:
        model = ContentBookmark
        fields = ['id', 'created_at']

    @staticmethod
    def resolve_content_name(obj):
        return obj.content.name
    
    @staticmethod
    def resolve_course_name(obj):
        return obj.content.course_id.name
    
    @staticmethod
    def resolve_content_description(obj):
        return obj.content.description

class ContentBookmarkIn(Schema):
    content_id: int

# Response Schemas
class MessageResponse(Schema):
    message: str
    
class ErrorResponse(Schema):
    error: str

class SuccessResponse(Schema):
    success: bool
    message: str
    data: Optional[dict] = None

class CategoryCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nama kategori")
    description: Optional[str] = Field(None, description="Deskripsi kategori")


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nama kategori")
    description: Optional[str] = Field(None, description="Deskripsi kategori")


class CategoryResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: str  # username
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nama kursus")
    description: str = Field(..., min_length=1, description="Deskripsi kursus")
    price: int = Field(..., ge=0, description="Harga kursus")
    category_id: Optional[int] = Field(None, description="ID kategori")


class CourseUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nama kursus")
    description: Optional[str] = Field(None, min_length=1, description="Deskripsi kursus")
    price: Optional[int] = Field(None, ge=0, description="Harga kursus")
    category_id: Optional[int] = Field(None, description="ID kategori")


class CourseResponseSchema(BaseModel):
    id: int
    name: str
    description: str
    price: int
    teacher: str  # username
    category: Optional[CategoryResponseSchema]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   