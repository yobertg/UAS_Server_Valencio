from locust import HttpUser, TaskSet, task, between
import json
import random
from datetime import datetime, timedelta

class UserBehavior(TaskSet):
    def on_start(self):
        """Initialize user session"""
        self.token = None
        self.user_id = None
        self.courses = []
        self.categories = []
        self.created_items = {
            'categories': [],
            'courses': [],
            'announcements': [],
            'comments': [],
            'feedback': [],
            'bookmarks': [],
            'completions': []
        }
        self.login()

    def login(self):
        """Login and get authentication token"""
        response = self.client.post("/auth/sign-in", json={
            "username": "MartinaKeiko", 
            "password": "RCI90BKE1IH" 
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access")
            print(f"✅ Login successful, token obtained")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")

    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    # ===== USER PROFILE ENDPOINTS =====
    
    @task(5)
    def get_current_user(self):
        """Test current user endpoint"""
        response = self.client.get("/current-user")
        if response.status_code == 200:
            print("✅ Current user retrieved")
        else:
            print(f"❌ Get current user failed: {response.status_code}")

    @task(3)
    def get_user_profile(self):
        """Test get user profile"""
        # Use a random user ID or current user ID
        user_id = random.randint(1, 10)  # Adjust range based on your data
        response = self.client.get(f"/profile/{user_id}")
        if response.status_code == 200:
            print(f"✅ Profile retrieved for user {user_id}")
        else:
            print(f"❌ Get profile failed for user {user_id}: {response.status_code}")

    @task(2)
    def update_profile(self):
        """Test update profile endpoint"""
        profile_data = {
            "first_name": f"TestUser{random.randint(1, 1000)}",
            "last_name": f"LastName{random.randint(1, 1000)}",
            "phone": f"08{random.randint(1000000000, 9999999999)}",
            "description": f"Test description {random.randint(1, 1000)}"
        }
        
        response = self.client.put("/profile", json=profile_data)
        if response.status_code == 200:
            print("✅ Profile updated successfully")
        else:
            print(f"❌ Profile update failed: {response.status_code}")

    # ===== CATEGORY ENDPOINTS =====
    
    @task(8)
    def create_category(self):
        """Test create category"""
        if not self.token:
            return
            
        category_data = {
            "name": f"Test Category {random.randint(1, 10000)}",
            "description": f"Test category description {random.randint(1, 10000)}"
        }
        
        response = self.client.post("/categories/", 
                                  json=category_data, 
                                  headers=self.get_headers())
        if response.status_code == 200:
            category_id = response.json().get("id")
            self.created_items['categories'].append(category_id)
            print(f"✅ Category created with ID: {category_id}")
        else:
            print(f"❌ Create category failed: {response.status_code} ")

    @task(10)
    def get_categories(self):
        """Test get all categories"""
        response = self.client.get("/categories/")
        if response.status_code == 200:
            self.categories = response.json()
            print(f"✅ Retrieved {len(self.categories)} categories")
        else:
            print(f"❌ Get categories failed: {response.status_code}")

    @task(5)
    def get_category_detail(self):
        """Test get category detail"""
        if self.categories:
            category = random.choice(self.categories)
            response = self.client.get(f"/categories/{category['id']}")
            if response.status_code == 200:
                print(f"✅ Category detail retrieved for ID: {category['id']}")
            else:
                print(f"❌ Get category detail failed: {response.status_code}")

    @task(3)
    def update_category(self):
        """Test update category"""
        if not self.token or not self.created_items['categories']:
            return
            
        category_id = random.choice(self.created_items['categories'])
        update_data = {
            "name": f"Updated Category {random.randint(1, 10000)}",
            "description": f"Updated description {random.randint(1, 10000)}"
        }
        
        response = self.client.put(f"/categories/{category_id}", 
                                 json=update_data, 
                                 headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Category {category_id} updated")
        else:
            print(f"❌ Update category failed: {response.status_code}")

    # ===== COURSE ENDPOINTS =====
    
    @task(7)
    def create_course(self):
        """Test create course"""
        if not self.token:
            return
            
        category_id = None
        if self.categories:
            category_id = random.choice(self.categories)['id']
            
        course_data = {
            "name": f"Test Course {random.randint(1, 10000)}",
            "description": f"Test course description {random.randint(1, 10000)}",
            "price": random.randint(100000, 1000000),
            "category_id": category_id
        }
        
        response = self.client.post("/courses/", 
                                  json=course_data, 
                                  headers=self.get_headers())
        if response.status_code == 200:
            course_id = response.json().get("id")
            self.created_items['courses'].append(course_id)
            print(f"✅ Course created with ID: {course_id}")
        else:
            print(f"❌ Create course failed: {response.status_code}")

    @task(10)
    def get_courses(self):
        """Test get all courses"""
        response = self.client.get("/courses/")
        if response.status_code == 200:
            self.courses = response.json()
            print(f"✅ Retrieved {len(self.courses)} courses")
        else:
            print(f"❌ Get courses failed: {response.status_code}")

    @task(3)
    def update_course(self):
        """Test update course"""
        if not self.token or not self.created_items['courses']:
            return
            
        course_id = random.choice(self.created_items['courses'])
        update_data = {
            "name": f"Updated Course {random.randint(1, 10000)}",
            "description": f"Updated description {random.randint(1, 10000)}",
            "price": random.randint(100000, 1000000)
        }
        
        response = self.client.put(f"/courses/{course_id}", 
                                 json=update_data, 
                                 headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Course {course_id} updated")
        else:
            print(f"❌ Update course failed: {response.status_code}")

    # ===== COURSE ANNOUNCEMENT ENDPOINTS =====
    
    @task(4)
    def create_announcement(self):
        """Test create announcement"""
        if not self.token or not self.created_items['courses']:
            return
            
        course_id = 1
        announcement_data = {
            "title": f"Test Announcement {random.randint(1, 10000)}",
            "content": f"Test announcement content {random.randint(1, 10000)}",
            "publish_date": (datetime.now() + timedelta(days=random.randint(0, 7))).isoformat(),
            "is_active": True
        }
        
        response = self.client.post(f"/courses/{course_id}/announcements", 
                                  json=announcement_data, 
                                  headers=self.get_headers())
        if response.status_code == 200:
            announcement_id = response.json().get("id")
            self.created_items['announcements'].append(announcement_id)
            print(f"✅ Announcement created with ID: {announcement_id}")
        else:
            print(f"❌ Create announcement failed: {response.status_code}")

    @task(6)
    def get_announcements(self):
        """Test get course announcements"""
        if not self.token or not self.courses:
            return
            
        course = random.choice(self.courses)
        course1 = 1
        response = self.client.get(f"/courses/{course1}/announcements", 
                                 headers=self.get_headers())
        if response.status_code == 200:
            announcements = response.json()
            print(f"✅ Retrieved {len(announcements)} announcements for course {course['id']}")
        else:
            print(f"❌ Get announcements failed: {response.status_code}")

    @task(2)
    def update_announcement(self):
        """Test update announcement"""
        if not self.token or not self.created_items['announcements']:
            return
            
        announcement_id = random.choice(self.created_items['announcements'])
        update_data = {
            "title": f"Updated Announcement {random.randint(1, 10000)}",
            "content": f"Updated content {random.randint(1, 10000)}",
            "is_active": random.choice([True, False])
        }
        
        response = self.client.put(f"/announcements/{announcement_id}", 
                                 json=update_data, 
                                 headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Announcement {announcement_id} updated")
        else:
            print(f"❌ Update announcement failed: {response.status_code}")

    # ===== CONTENT COMPLETION ENDPOINTS =====
    
    @task(4)
    def add_completion(self):
        """Test add content completion"""
        if not self.token:
            return
            
        # Assuming content IDs exist (you may need to adjust this)
        content_id = random.randint(1, 100)
        completion_data = {
            "content_id": content_id
        }
        
        response = self.client.post("/content/completion", 
                                  json=completion_data, 
                                  headers=self.get_headers())
        if response.status_code == 200:
            completion_id = response.json().get("id")
            self.created_items['completions'].append(completion_id)
            print(f"✅ Completion tracking added for content {content_id}")
        elif response.status_code == 400:
            print("ℹ️ Content already marked as completed")
        else:
            print(f"❌ Add completion failed: {response.status_code}")

    @task(3)
    def get_completions(self):
        """Test get course completions"""
        if not self.token or not self.courses:
            return
            
        course = random.choice(self.courses)
        response = self.client.get(f"/courses/{course['id']}/completions", 
                                 headers=self.get_headers())
        if response.status_code == 200:
            completions = response.json()
            print(f"✅ Retrieved {len(completions)} completions for course {course['id']}")
        else:
            print(f"❌ Get completions failed: {response.status_code}")

    # ===== FEEDBACK ENDPOINTS =====
    
    @task(4)
    def add_feedback(self):
        """Test add course feedback"""
        if not self.token or not self.courses:
            return
            
        course = random.choice(self.courses)
        feedback_data = {
            "course_id": course['id'],
            "rating": random.randint(1, 5),
            "feedback_text": f"Test feedback {random.randint(1, 10000)}"
        }
        
        response = self.client.post("/feedback", 
                                  json=feedback_data, 
                                  headers=self.get_headers())
        if response.status_code == 200:
            feedback_id = response.json().get("id")
            self.created_items['feedback'].append(feedback_id)
            print(f"✅ Feedback added for course {course['id']}")
        else:
            print(f"❌ Add feedback failed: {response.status_code}")

    @task(5)
    def get_feedback(self):
        """Test get course feedback"""
        if not self.token or not self.courses:
            return
            
        course = random.choice(self.courses)
        response = self.client.get(f"/courses/{course['id']}/feedback", 
                                 headers=self.get_headers())
        if response.status_code == 200:
            feedback_list = response.json()
            print(f"✅ Retrieved {len(feedback_list)} feedback for course {course['id']}")
        else:
            print(f"❌ Get feedback failed: {response.status_code}")

    @task(2)
    def update_feedback(self):
        """Test update feedback"""
        if not self.token or not self.created_items['feedback']:
            return
            
        feedback_id = random.choice(self.created_items['feedback'])
        update_data = {
            "rating": random.randint(1, 5),
            "feedback_text": f"Updated feedback {random.randint(1, 10000)}"
        }
        
        response = self.client.put(f"/feedback/{feedback_id}", 
                                 json=update_data, 
                                 headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Feedback {feedback_id} updated")
        else:
            print(f"❌ Update feedback failed: {response.status_code}")

    # ===== BOOKMARK ENDPOINTS =====
    
    @task(3)
    def add_bookmark(self):
        """Test add content bookmark"""
        if not self.token:
            return
            
        # Assuming content IDs exist (you may need to adjust this)
        content_id = 47
        bookmark_data = {
            "content_id": content_id
        }
        
        response = self.client.post("/bookmark", 
                                  json=bookmark_data, 
                                  headers=self.get_headers())
        if response.status_code == 200:
            bookmark_id = response.json().get("id")
            self.created_items['bookmarks'].append(bookmark_id)
            print(f"✅ Bookmark added for content {content_id}")
        elif response.status_code == 400:
            print("ℹ️ Content already bookmarked")
        else:
            print(f"❌ Add bookmark failed: {response.status_code}")

    @task(4)
    def get_bookmarks(self):
        """Test get user bookmarks"""
        if not self.token:
            return
            
        response = self.client.get("/bookmarks", headers=self.get_headers())
        if response.status_code == 200:
            bookmarks = response.json()
            print(f"✅ Retrieved {len(bookmarks)} bookmarks")
        else:
            print(f"❌ Get bookmarks failed: {response.status_code}")

    # ===== CLEANUP TASKS (Lower weight) =====
    
    @task(1)
    def delete_announcement(self):
        """Test delete announcement"""
        if not self.token or not self.created_items['announcements']:
            return
            
        announcement_id = self.created_items['announcements'].pop()
        response = self.client.delete(f"/announcements/{announcement_id}", 
                                    headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Announcement {announcement_id} deleted")
        else:
            print(f"❌ Delete announcement failed: {response.status_code}")

    @task(1)
    def delete_completion(self):
        """Test delete completion"""
        if not self.token or not self.created_items['completions']:
            return
            
        completion_id = self.created_items['completions'].pop()
        response = self.client.delete(f"/completions/{completion_id}", 
                                    headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Completion {completion_id} deleted")
        else:
            print(f"❌ Delete completion failed: {response.status_code}")

    @task(1)
    def delete_feedback(self):
        """Test delete feedback"""
        if not self.token or not self.created_items['feedback']:
            return
            
        feedback_id = self.created_items['feedback'].pop()
        response = self.client.delete(f"/feedback/{feedback_id}", 
                                    headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Feedback {feedback_id} deleted")
        else:
            print(f"❌ Delete feedback failed: {response.status_code}")

    @task(1)
    def delete_bookmark(self):
        """Test delete bookmark"""
        if not self.token or not self.created_items['bookmarks']:
            return
            
        bookmark_id = self.created_items['bookmarks'].pop()
        response = self.client.delete(f"/bookmarks/{bookmark_id}", 
                                    headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Bookmark {bookmark_id} deleted")
        else:
            print(f"❌ Delete bookmark failed: {response.status_code}")

    @task(1)
    def delete_category(self):
        """Test delete category"""
        if not self.token or not self.created_items['categories']:
            return
            
        category_id = self.created_items['categories'].pop()
        response = self.client.delete(f"/categories/{category_id}", 
                                    headers=self.get_headers())
        if response.status_code == 200:
            print(f"✅ Category {category_id} deleted")
        else:
            print(f"❌ Delete category failed: {response.status_code}")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    # You can configure different user types with different behaviors
    # Example: Teacher vs Student behavior
    weight = 1  # Relative weight for this user type


# Optional: Create different user types for different roles
class TeacherUser(HttpUser):
    """User type focused on teacher-specific tasks"""
    tasks = [UserBehavior]
    wait_time = between(2, 5)
    weight = 1
    
    def on_start(self):
        # Could implement teacher-specific login here
        pass


class StudentUser(HttpUser):
    """User type focused on student-specific tasks"""  
    tasks = [UserBehavior]
    wait_time = between(1, 3)
    weight = 3  # More students than teachers
    
    def on_start(self):
        # Could implement student-specific login here
        pass