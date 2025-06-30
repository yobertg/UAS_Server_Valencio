import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, *[os.pardir] * 3)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'simplelms.settings'
import django
django.setup()

import csv
import json
from random import randint
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from lms_core.models import Course, CourseMember, CourseContent, Comment, CourseAnnouncement, ContentCompletion, CourseFeedback, ContentBookmark, UserProfile

import time
start_time = time.time()

filepath = './csv_data/'

# Import Users
print("Importing Users...")
with open(filepath+'user-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    for num, row in enumerate(reader):
        if not User.objects.filter(username=row['username']).exists():
            obj_create.append(User(username=row['username'], 
                                     password=make_password(row['password']), 
                                     email=row['email'],
                                     first_name=row['firstname'],
                                     last_name=row['lastname']))
    User.objects.bulk_create(obj_create)
print(f"Users imported: {len(obj_create)}")

# Import Courses
print("Importing Courses...")
with open(filepath+'course-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    for num,row in enumerate(reader):
        if not Course.objects.filter(pk=num+1).exists():
            obj_create.append(Course(name=row['name'], price=row['price'],
                                  description=row['description'], 
                                  teacher=User.objects.get(pk=int(row['teacher']))))
    Course.objects.bulk_create(obj_create)
print(f"Courses imported: {len(obj_create)}")

# Import Course Members - FIXED VERSION
print("Importing Course Members...")
with open(filepath+'member-data.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    obj_create = []
    existing_combinations = set()  # Track existing course-user combinations
    
    for num, row in enumerate(reader):
        course_id = int(row['course_id'])
        user_id = int(row['user_id'])
        combination = (course_id, user_id)
        
        # Check if this combination already exists in database or in current batch
        if (combination not in existing_combinations and 
            not CourseMember.objects.filter(course_id=course_id, user_id=user_id).exists()):
            
            try:
                course = Course.objects.get(pk=course_id)
                user = User.objects.get(pk=user_id)
                
                obj_create.append(CourseMember(course_id=course,
                                            user_id=user, 
                                            roles=row['roles']))
                existing_combinations.add(combination)
            except (Course.DoesNotExist, User.DoesNotExist) as e:
                print(f"Skipping member {num+1}: {e}")
                continue
        else:
            print(f"Skipping duplicate course-user combination: Course {course_id}, User {user_id}")
    
    CourseMember.objects.bulk_create(obj_create)
print(f"Course Members imported: {len(obj_create)}")

# Import Course Contents
print("Importing Course Contents...")
with open(filepath+'contents.json') as jsonfile:
    contents = json.load(jsonfile)
    obj_create = []
    for num, row in enumerate(contents):
        if not CourseContent.objects.filter(pk=num+1).exists():
            try:
                course = Course.objects.get(pk=int(row['course_id']))
                obj_create.append(CourseContent(course_id=course, 
                                             video_url=row['video_url'], name=row['name'], 
                                             description=row['description']))
            except Course.DoesNotExist as e:
                print(f"Skipping content {num+1}: {e}")
                continue
    CourseContent.objects.bulk_create(obj_create)
print(f"Course Contents imported: {len(obj_create)}")

# Import Comments
print("Importing Comments...")
with open(filepath+'comments.json') as jsonfile:
    comments = json.load(jsonfile)
    obj_create = []
    for num, row in enumerate(comments):
        if int(row['user_id']) > 50:
            row['user_id'] = randint(5, 40)
        if not Comment.objects.filter(pk=num+1).exists():
            try:
                content = CourseContent.objects.get(pk=int(row['content_id']))
                user = User.objects.get(pk=int(row['user_id']))
                
                # Find the CourseMember instance for this user and course
                course_member = CourseMember.objects.filter(
                    user_id=user, 
                    course_id=content.course_id
                ).first()
                
                if course_member:
                    obj_create.append(Comment(content_id=content, 
                                           member_id=course_member, 
                                           comment=row['comment']))
                else:
                    print(f"Skipping comment {num+1}: User {user.username} is not a member of course {content.course_id.name}")
                    
            except (CourseContent.DoesNotExist, User.DoesNotExist) as e:
                print(f"Skipping comment {num+1}: {e}")
                continue
    Comment.objects.bulk_create(obj_create)
print(f"Comments imported: {len(obj_create)}")

# Function to parse ISO datetime string
def parse_datetime(datetime_str):
    """Parse ISO format datetime string to Django timezone aware datetime"""
    if datetime_str:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        # Check if datetime is already timezone-aware
        if dt.tzinfo is not None:
            return dt
        else:
            return timezone.make_aware(dt)
    return None
# Import Course Announcements
print("Importing Course Announcements...")
try:
    with open(filepath+'dummyData.json') as jsonfile:
        data = json.load(jsonfile)
        obj_create = []
        
        for announcement in data['course_announcements']:
            if not CourseAnnouncement.objects.filter(pk=announcement['id']).exists():
                try:
                    course = Course.objects.get(pk=announcement['course'])
                    teacher = User.objects.get(pk=announcement['teacher'])
                    
                    obj_create.append(CourseAnnouncement(
                        id=announcement['id'],
                        course=course,
                        title=announcement['title'],
                        content=announcement['content'],
                        is_active=announcement['is_active'],
                        created_at=parse_datetime(announcement['created_at']),
                        updated_at=parse_datetime(announcement['updated_at']),
                        teacher=teacher,  # Assuming teacher is the creator
                        publish_date=parse_datetime(announcement['publish_date'])
                    ))
                except (Course.DoesNotExist, User.DoesNotExist) as e:
                    print(f"Skipping announcement {announcement['id']}: {e}")
                    continue
        
        CourseAnnouncement.objects.bulk_create(obj_create)
        print(f"Course Announcements imported: {len(obj_create)}")
except FileNotFoundError:
    print("dummyData.json not found, skipping Course Announcements")
except Exception as e:
    print(f"Error importing Course Announcements: {e}")

# Import Content Completions
print("Importing Content Completions...")
try:
    with open(filepath+'dummyData.json') as jsonfile:
        data = json.load(jsonfile)
        obj_create = []
        existing_combinations = set()  # Track existing user-content combinations
        
        for completion in data['content_completions']:
            user_id = completion['student']
            content_id = completion['content']
            combination = (user_id, content_id)
            
            if (combination not in existing_combinations and 
                not ContentCompletion.objects.filter(student=user_id, content=content_id).exists()):
                
                try:
                    user = User.objects.get(pk=user_id)
                    content = CourseContent.objects.get(pk=content_id)
                    # Get course from content
                    course = content.course_id
                    
                    obj_create.append(ContentCompletion(
                        id=completion['id'],
                        student=user,
                        content=content,
                        completed_at=parse_datetime(completion['completed_at']),  # Assuming completed means 100%
                    ))
                    existing_combinations.add(combination)
                except (User.DoesNotExist, CourseContent.DoesNotExist) as e:
                    print(f"Skipping completion {completion['id']}: {e}")
                    continue
            else:
                print(f"Skipping duplicate completion: User {user_id}, Content {content_id}")
        
        ContentCompletion.objects.bulk_create(obj_create)
        print(f"Content Completions imported: {len(obj_create)}")
except FileNotFoundError:
    print("dummyData.json not found, skipping Content Completions")
except Exception as e:
    print(f"Error importing Content Completions: {e}")

# Import Course Feedbacks
print("Importing Course Feedbacks...")
try:
    with open(filepath+'dummyData.json') as jsonfile:
        data = json.load(jsonfile)
        obj_create = []
        existing_combinations = set()  # Track existing user-course combinations for feedback
        
        for feedback in data['course_feedbacks']:
            user_id = feedback['student']
            course_id = feedback['course']
            combination = (user_id, course_id)
            
            if (combination not in existing_combinations and 
                not CourseFeedback.objects.filter(student=user_id, course=course_id).exists()):
                
                try:
                    user = User.objects.get(pk=user_id)
                    course = Course.objects.get(pk=course_id)
                    
                    obj_create.append(CourseFeedback(
                        id=feedback['id'],
                        student=user,
                        course=course,
                        rating=feedback['rating'],
                        feedback_text=feedback['feedback_text'],
                        created_at=parse_datetime(feedback['created_at']),
                        updated_at=parse_datetime(feedback['updated_at'])
                    ))
                    existing_combinations.add(combination)
                except (User.DoesNotExist, Course.DoesNotExist) as e:
                    print(f"Skipping feedback {feedback['id']}: {e}")
                    continue
            else:
                print(f"Skipping duplicate feedback: User {user_id}, Course {course_id}")
        
        CourseFeedback.objects.bulk_create(obj_create)
        print(f"Course Feedbacks imported: {len(obj_create)}")
except FileNotFoundError:
    print("dummyData.json not found, skipping Course Feedbacks")
except Exception as e:
    print(f"Error importing Course Feedbacks: {e}")

# Import Content Bookmarks
print("Importing Content Bookmarks...")
try:
    with open(filepath+'dummyData.json') as jsonfile:
        data = json.load(jsonfile)
        obj_create = []
        existing_combinations = set()  # Track existing user-content combinations for bookmarks
        
        for bookmark in data['content_bookmarks']:
            user_id = bookmark['student']
            content_id = bookmark['content']
            combination = (user_id, content_id)
            
            if (combination not in existing_combinations and 
                not ContentBookmark.objects.filter(student=user_id, content=content_id).exists()):
                
                try:
                    user = User.objects.get(pk=user_id)
                    content = CourseContent.objects.get(pk=content_id)
                    # Get course from content
                    
                    
                    obj_create.append(ContentBookmark(
                        id=bookmark['id'],
                        student=user,
                        content=content,
                        created_at=parse_datetime(bookmark['created_at']), # Default value since not in sample data
                    ))
                    existing_combinations.add(combination)
                except (User.DoesNotExist, CourseContent.DoesNotExist) as e:
                    print(f"Skipping bookmark {bookmark['id']}: {e}")
                    continue
            else:
                print(f"Skipping duplicate bookmark: User {user_id}, Content {content_id}")
        
        ContentBookmark.objects.bulk_create(obj_create)
        print(f"Content Bookmarks imported: {len(obj_create)}")
except FileNotFoundError:
    print("dummyData.json not found, skipping Content Bookmarks")
except Exception as e:
    print(f"Error importing Content Bookmarks: {e}")

# Import User Profiles
print("Importing User Profiles...")
try:
    with open(filepath+'dummyData.json') as jsonfile:
        data = json.load(jsonfile)
        obj_create = []
        existing_user_ids = set()  # Track existing user IDs to avoid duplicates
        
        for profile in data['user_profiles']:
            user_id = profile['user']
            
            # Check if profile already exists in database or in current batch
            if (user_id not in existing_user_ids and 
                not UserProfile.objects.filter(user=user_id).exists() and
                not UserProfile.objects.filter(pk=profile['id']).exists()):
                
                try:
                    user = User.objects.get(pk=user_id)
                    
                    obj_create.append(UserProfile(
                        id=profile['id'],
                        user=user,
                        phone=profile['phone'],
                        description=profile['description'],
                        profile_picture=profile['profile_picture'],
                        created_at=parse_datetime(profile['created_at']),
                        updated_at=parse_datetime(profile['updated_at'])
                    ))
                    existing_user_ids.add(user_id)
                except User.DoesNotExist as e:
                    print(f"Skipping profile {profile['id']}: User {user_id} does not exist")
                    continue
            else:
                print(f"Skipping duplicate user profile: User {user_id} already has a profile")
        
        UserProfile.objects.bulk_create(obj_create)
        print(f"User Profiles imported: {len(obj_create)}")
except FileNotFoundError:
    print("paste.txt not found, skipping User Profiles")
except Exception as e:
    print(f"Error importing User Profiles: {e}")

print("--- %s seconds ---" % (time.time() - start_time))
print("All imports completed!")