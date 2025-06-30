from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Category(models.Model):
    name = models.CharField("Nama Kategori", max_length=100, unique=True)
    description = models.TextField("Deskripsi", blank=True, null=True)
    created_by = models.ForeignKey(User, verbose_name="Dibuat oleh", on_delete=models.CASCADE)
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Data Kategori"
        ordering = ["name"]
        
class Course(models.Model):
    name = models.CharField("Nama Kursus", max_length=255)
    description = models.TextField("Deskripsi")
    price = models.IntegerField("Harga")
    image = models.ImageField("Gambar", upload_to="course/", blank=True, null=True)
    teacher = models.ForeignKey(User, verbose_name="Pengajar", on_delete=models.RESTRICT)
    category = models.ForeignKey(Category, verbose_name="Kategori", on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Data Mata Kuliah"
        ordering = ["-created_at"]

    def is_member(self, user):
        return CourseMember.objects.filter(course_id=self, user_id=user).exists()
    
    def clean(self):
        if self.price < 0:
            raise ValidationError({'price': 'Harga tidak boleh negatif'})

ROLE_OPTIONS = [('std', "Siswa"), ('ast', "Asisten")]




class CourseMember(models.Model):
    # Tetap menggunakan nama field lama untuk kompatibilitas
    course_id = models.ForeignKey(Course, verbose_name="Mata Kuliah", on_delete=models.RESTRICT)
    user_id = models.ForeignKey(User, verbose_name="Pengguna", on_delete=models.RESTRICT)
    roles = models.CharField("Peran", max_length=3, choices=ROLE_OPTIONS, default='std')
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Anggota Mata Kuliah"
        verbose_name_plural = "Anggota Mata Kuliah"
        unique_together = ['course_id', 'user_id']  # Prevent duplicate memberships

    def __str__(self) -> str:
        return f"{self.course_id.name} - {self.user_id.username} ({self.get_roles_display()})"

class CourseContent(models.Model):
    name = models.CharField("Judul Konten", max_length=200)
    description = models.TextField("Deskripsi", default='-')
    video_url = models.URLField('URL Video', max_length=500, null=True, blank=True)
    file_attachment = models.FileField("File", upload_to="course_content/", null=True, blank=True)
    course_id = models.ForeignKey(Course, verbose_name="Mata Kuliah", on_delete=models.RESTRICT, related_name='contents')
    parent_id = models.ForeignKey("self", verbose_name="Induk", 
                              on_delete=models.RESTRICT, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Konten Mata Kuliah"
        verbose_name_plural = "Konten Mata Kuliah"
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'{self.course_id.name} - {self.name}'

    def clean(self):
        # Prevent self-referencing parent
        if self.parent_id == self:
            raise ValidationError({'parent_id': 'Konten tidak boleh menjadi induk dari dirinya sendiri'})

class Comment(models.Model):
    content_id = models.ForeignKey(CourseContent, verbose_name="Konten", on_delete=models.CASCADE, related_name='comments')
    member_id = models.ForeignKey(CourseMember, verbose_name="Anggota", on_delete=models.CASCADE)
    comment = models.TextField('Komentar')
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)
    
    class Meta:
        verbose_name = "Komentar"
        verbose_name_plural = "Komentar"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Komentar oleh {self.member_id.user_id.username} pada {self.content_id.name}"
    
    def clean(self):
        # Ensure the member belongs to the course of the content
        if self.content_id.course_id != self.member_id.course_id:
            raise ValidationError('Anggota harus terdaftar di mata kuliah yang sama dengan konten')

# Extend User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(
        "Handphone", 
        max_length=15, 
        blank=True, 
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format nomor telepon tidak valid")]
    )
    description = models.TextField("Deskripsi", blank=True, null=True)
    profile_picture = models.ImageField("Foto Profil", upload_to="profiles/", blank=True, null=True)
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Profil Pengguna"
        verbose_name_plural = "Profil Pengguna"

    def __str__(self):
        return f"Profile of {self.user.username}"

# Course Announcements
class CourseAnnouncement(models.Model):
    course = models.ForeignKey(Course, verbose_name="Kursus", on_delete=models.CASCADE, related_name='announcements')
    teacher = models.ForeignKey(User, verbose_name="Pengajar", on_delete=models.CASCADE)
    title = models.CharField("Judul Pengumuman", max_length=255)
    content = models.TextField("Isi Pengumuman")
    publish_date = models.DateTimeField("Tanggal Publikasi")
    is_active = models.BooleanField("Aktif", default=True)
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Pengumuman Kursus"
        verbose_name_plural = "Pengumuman Kursus"
        ordering = ["-publish_date"]

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    def clean(self):
        # Ensure teacher is the course teacher or course member with assistant role
        if self.teacher != self.course.teacher:
            if not CourseMember.objects.filter(course=self.course, user=self.teacher, roles='ast').exists():
                raise ValidationError('Hanya pengajar atau asisten yang dapat membuat pengumuman')

# Content Completion Tracking
class ContentCompletion(models.Model):
    student = models.ForeignKey(User, verbose_name="Siswa", on_delete=models.CASCADE)
    content = models.ForeignKey(CourseContent, verbose_name="Konten", on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField("Diselesaikan pada", auto_now_add=True)
    
    class Meta:
        verbose_name = "Penyelesaian Konten"
        verbose_name_plural = "Penyelesaian Konten"
        unique_together = ['student', 'content']  # Prevent duplicate completions

    def __str__(self):
        return f"{self.student.username} completed {self.content.name}"

    def clean(self):
        # Ensure student is a member of the course
        if not CourseMember.objects.filter(course=self.content.course, user=self.student).exists():
            raise ValidationError('Siswa harus terdaftar di mata kuliah ini')

# Course Feedback
class CourseFeedback(models.Model):
    RATING_CHOICES = [
        (1, '1 - Sangat Buruk'),
        (2, '2 - Buruk'),
        (3, '3 - Cukup'),
        (4, '4 - Baik'),
        (5, '5 - Sangat Baik'),
    ]
    
    course = models.ForeignKey(Course, verbose_name="Kursus", on_delete=models.CASCADE, related_name='feedbacks')
    student = models.ForeignKey(User, verbose_name="Siswa", on_delete=models.CASCADE)
    rating = models.IntegerField("Rating", choices=RATING_CHOICES)
    feedback_text = models.TextField("Umpan Balik")
    created_at = models.DateTimeField("Dibuat pada", auto_now_add=True)
    updated_at = models.DateTimeField("Diperbarui pada", auto_now=True)

    class Meta:
        verbose_name = "Umpan Balik Kursus"
        verbose_name_plural = "Umpan Balik Kursus"
        unique_together = ['course', 'student']  # One feedback per student per course

    def __str__(self):
        return f"Feedback by {self.student.username} for {self.course.name}"

    def clean(self):
        # Ensure student is a member of the course
        if not CourseMember.objects.filter(course=self.course, user=self.student).exists():
            raise ValidationError('Siswa harus terdaftar di mata kuliah ini untuk memberikan feedback')

# Content Bookmarking
class ContentBookmark(models.Model):
    student = models.ForeignKey(User, verbose_name="Siswa", on_delete=models.CASCADE)
    content = models.ForeignKey(CourseContent, verbose_name="Konten", on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField("Dibookmark pada", auto_now_add=True)

    class Meta:
        verbose_name = "Bookmark Konten"
        verbose_name_plural = "Bookmark Konten"
        unique_together = ['student', 'content']  # Prevent duplicate bookmarks

    def __str__(self):
        return f"{self.student.username} bookmarked {self.content.name}"
    
    def clean(self):
        # Ensure student is a member of the course
        if not CourseMember.objects.filter(course=self.content.course, user=self.student).exists():
            raise ValidationError('Siswa harus terdaftar di mata kuliah ini untuk mem-bookmark konten')