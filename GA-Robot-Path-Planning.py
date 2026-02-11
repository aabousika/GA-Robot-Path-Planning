import random  # مكتبة لإنشاء أرقام عشوائية
import matplotlib.pyplot as plt  # مكتبة لإنشاء الرسوم البيانية
import copy  # مكتبة لنسخ الكائنات بعمق
import math  # مكتبة للعمليات الرياضية
import time  # مكتبة للتعامل مع الوقت
import numpy as np  # مكتبة للعمليات الرياضية المتقدمة
import matplotlib.patches as patches  # لإضافة أشكال هندسية للرسم
from matplotlib.animation import FuncAnimation  # لإنشاء رسوم متحركة
import matplotlib  # المكتبة الرئيسية للرسم
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox ,scrolledtext
import matplotlib
# ⭐⭐ إضافة هذه السطر قبل أي استيراد لـ matplotlib ⭐⭐
matplotlib.use('TkAgg')  # استخدام backend مناسب لـ Tkinter
from tkinter import simpledialog


class Obstacle:
    def __init__(self, vertices, is_dynamic=False, velocity=None):
        """تهيئة عقبة جديدةﬁ
        
        المعاملات:
        vertices: قائمة من النقاط (إحداثيات) تمثل زوايا العقبة
        is_dynamic: إذا كانت العقبة متحركة أم ثابتة
        velocity: سرعة الحركة إذا كانت العقبة متحركة
        """
        self.vertices = vertices  # تخزين قائمة النقاط (الزوايا) في خاصية الكائن
        self.is_dynamic = is_dynamic  # تخزين حالة الحركة (ثابتة أم متحركة)
        self.velocity = velocity if velocity else (0, 0)  # إذا لم يتم تحديد سرعة، استخدم (0,0)
        self.original_vertices = copy.deepcopy(vertices)  # نسخة احتياطية من الإحداثيات الأصلية
    
    def contains_point(self, x, y):
        """التحقق إذا كانت النقطة (x, y) داخل العقبة المضلعة
        
        الخوارزمية: خوارزمية "Ray Casting" لاختبار إذا كانت النقطة داخل مضلع
        """
        n = len(self.vertices)  # حساب عدد زوايا المضلع
        inside = False  # افتراض أن النقطة خارج المضلع
        p1x, p1y = self.vertices[0]  # أخذ أول نقطة في المضلع
        for i in range(n + 1):  # حلقة تمر على جميع أضلاع المضلع + ضلع إضافي للإغلاق
            p2x, p2y = self.vertices[i % n]  # أخذ النقطة التالية (i % n تضمن العودة للنقطة الأولى)
            if y > min(p1y, p2y):  # التحقق إذا كانت النقطة أعلى من الطرف الأدنى للضلع
                if y <= max(p1y, p2y):  # التحقق إذا كانت النقطة أسفل أو عند الطرف الأعلى للضلع
                    if x <= max(p1x, p2x):  # التحقق إذا كانت النقطة على يسار أو عند أقصى نقطة في الضلع
                        if p1y != p2y:  # التحقق إذا كان الضلع غير أفقي
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x  # حساب تقاطع شعاع أفقي
                        if p1x == p2x or x <= xinters:  # إذا كان الضلع رأسياً أو النقطة على يسار التقاطع
                            inside = not inside  # تغيير حالة inside (التبديل)
            p1x, p1y = p2x, p2y  # تحضير للضلع التالي (النقطة الثانية تصبح الأولى)
        return inside  # إرجاع النتيجة النهائية
    
    def update_position(self):
        """تحديث موقع العقبة المتحركة ومعالجة الاصطدام بالحدود"""
        if not self.is_dynamic:  # إذا كانت العقبة غير متحركة
            return  # خروج فوري من الدالة
        
        dx, dy = self.velocity  # فك سرعة الحركة إلى مكونين
        for i in range(len(self.vertices)):  # تحديث جميع نقاط المضلع
            self.vertices[i] = (self.vertices[i][0] + dx, self.vertices[i][1] + dy)  # إضافة السرعة للإحداثيات
            
        # Boundary checking - bounce back if hitting boundaries
        min_x = min(v[0] for v in self.vertices)  # إيجاد أصغر قيمة X
        max_x = max(v[0] for v in self.vertices)  # إيجاد أكبر قيمة X
        min_y = min(v[1] for v in self.vertices)  # إيجاد أصغر قيمة Y
        max_y = max(v[1] for v in self.vertices)  # إيجاد أكبر قيمة Y
        
        if min_x < 0 or max_x > 100:  # التحقق من الاصطدام بالحدود الأفقية
            self.velocity = (-self.velocity[0], self.velocity[1])  # عكس اتجاه الحركة الأفقية
            # Move back to valid position
            for i in range(len(self.vertices)):
                # إرجاع العقبة داخل الحدود باستخدام max و min
                self.vertices[i] = (max(0, min(self.vertices[i][0], 100)), self.vertices[i][1])
        if min_y < 0 or max_y > 100:  # التحقق من الاصطدام بالحدود الرأسية
            self.velocity = (self.velocity[0], -self.velocity[1])  # عكس اتجاه الحركة الرأسية
            # Move back to valid position
            for i in range(len(self.vertices)):
                # إرجاع العقبة داخل الحدود
                self.vertices[i] = (self.vertices[i][0], max(0, min(self.vertices[i][1], 100)))

class Environment:
    def __init__(self, width=100, height=100):
        """تهيئة بيئة جديدة للروبوت"""
        self.width = width  # تخزين عرض البيئة
        self.height = height  # تخزين ارتفاع البيئة
        self.obstacles = []  # إنشاء قائمة فارغة لتخزين جميع العقبات
        self.dynamic_obstacles = []  # إنشاء قائمة فارغة للعقبات المتحركة فقط
        self.start = None  # تهيئة نقطة البداية بقيمة None
        self.goal = None  # تهيئة نقطة الهدف بقيمة None
        self.time_step = 0  # تهيئة عداد الخطوات الزمنية بصفر
    
    def add_obstacle(self, obstacle):
        """إضافة عقبة إلى البيئة"""
        self.obstacles.append(obstacle)  # إضافة العقبة إلى القائمة العامة
        if obstacle.is_dynamic:  # إذا كانت العقبة متحركة
            self.dynamic_obstacles.append(obstacle)  # أضفها أيضاً لقائمة العقبات المتحركة
    
    def add_random_obstacle(self, size=5, is_dynamic=False):
        """إضافة عقبة عشوائية إلى البيئة"""
        max_attempts = 50  # تحديد عدد المحاولات القصوى لتوليد عقبة صالحة
        for attempt in range(max_attempts):  # تكرار حتى 50 مرة لمحاولة إنشاء عقبة صالحة
            # توليد إحداثيات X و Y عشوائية مع هوامش
            x = random.randint(10, self.width - size - 10)
            y = random.randint(10, self.height - size - 10)
            
            # تعريف زوايا المربع (4 نقاط)
            vertices = [
                (x, y), (x + size, y), 
                (x + size, y + size), (x, y + size)
            ]
            
            obstacle_valid = True  # افتراض أن العقبة صالحة (قيمة أولية)
            temp_obstacle = Obstacle(vertices)  # إنشاء عقبة مؤقتة للاختبار
            
            # التحقق إذا كانت العقبة تغطي نقطة البداية
            if self.start and temp_obstacle.contains_point(self.start[0], self.start[1]):
                obstacle_valid = False  # جعل العقبة غير صالحة
            
            # التحقق إذا كانت العقبة تغطي نقطة الهدف
            if self.goal and temp_obstacle.contains_point(self.goal[0], self.goal[1]):
                obstacle_valid = False  # جعل العقبة غير صالحة
            
            if obstacle_valid:  # إذا كانت العقبة صالحة
                if is_dynamic:  # إذا كانت العقبة متحركة
                    # توليد سرعة عشوائية بين -0.8 و 0.8
                    velocity = (random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8))
                    obstacle = Obstacle(vertices, is_dynamic=True, velocity=velocity)  # إنشاء عقبة متحركة
                else:
                    obstacle = Obstacle(vertices, is_dynamic=False)  # إنشاء عقبة ثابتة
                
                self.add_obstacle(obstacle)  # إضافة العقبة للبيئة
                return obstacle  # إرجاع العقبة المُنشأة
        
        return None  # إذا فشلت جميع المحاولات، أرجع None
    
    def set_start_goal(self, start_x, start_y, goal_x, goal_y):
        """تعيين نقطة البداية والهدف"""
        self.start = (start_x, start_y)  # تخزين نقطة البداية
        self.goal = (goal_x, goal_y)  # تخزين نقطة الهدف
    
    def is_point_feasible(self, x, y):
        """التحقق إذا كانت النقطة ممكنة (لا تصطدم بعقبة وضمن الحدود)"""
        if x < 0 or x > self.width or y < 0 or y > self.height:  # التحقق من حدود البيئة
            return False  # النقطة خارج الحدود
        
        for obstacle in self.obstacles:  # التكرار على جميع العقبات
            if obstacle.contains_point(x, y):  # إذا كانت العقبة تحتوي على النقطة
                return False  # النقطة غير ممكنة
        
        return True  # النقطة ممكنة
    
    def is_line_feasible(self, point1, point2):
        """التحقق إذا كان الخط بين نقطتين ممكناً (لا يتقاطع مع عقبات)"""
        for obstacle in self.obstacles:  # التكرار على جميع العقبات
            if self.does_line_intersect_polygon(point1, point2, obstacle.vertices):  # إذا كان الخط يتقاطع مع العقبة
                return False  # الخط غير ممكن
        return True  # الخط ممكن
    
    def does_line_intersect_polygon(self, point1, point2, vertices):
        """التحقق إذا كان الخط يتقاطع مع مضلع"""
        n = len(vertices)  # حساب عدد زوايا المضلع
        for i in range(n):  # التكرار على جميع أضلاع المضلع
            p1 = vertices[i]  # أخذ النقطة الأولى للضلع
            p2 = vertices[(i + 1) % n]  # أخذ النقطة الثانية للضلع
            if self.do_lines_intersect(point1, point2, p1, p2):  # إذا تقاطع الخط مع هذا الضلع
                return True  # هناك تقاطع
        return False  # لا يوجد تقاطع
    
    def do_lines_intersect(self, p1, p2, q1, q2):
        """التحقق إذا كان خطان يتقاطعان باستخدام خوارزمية CCW"""
        def ccw(A, B, C):
            """دالة مساعدة تحدد اتجاه الثلاث نقاط (Counter Clock Wise)"""
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
        
        # الشرط: p1 و p2 على جانبي الخط (q1,q2) المختلف و q1 و q2 على جانبي الخط (p1,p2) المختلف
        return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)
    
    def update_dynamic_obstacles(self):
        """تحديث مواقع جميع العقبات المتحركة"""
        for obstacle in self.dynamic_obstacles:  # التكرار على العقبات المتحركة
            obstacle.update_position()  # تحديث موقع العقبة
        self.time_step += 1  # زيادة عداد الزمن بمقدار 1

    def visualize(self, chromosomes=None, robot_position=None, trail=None, title='Robot Path Planning Environment'):
        """رسم البيئة مع المسارات والروبوت"""
        plt.figure(figsize=(12, 10))  # إنشاء نافذة رسم جديدة بحجم 12×10 بوصة
        
        # رسم العقبات
        for obstacle in self.obstacles:
            vertices = obstacle.vertices  # أخذ زوايا العقبة
            x_coords = [v[0] for v in vertices] + [vertices[0][0]]  # استخراج إحداثيات X وإضافة الأولى للإغلاق
            y_coords = [v[1] for v in vertices] + [vertices[0][1]]  # استخراج إحداثيات Y وإضافة الأولى للإغلاق
            
            color = 'orange' if obstacle.is_dynamic else 'red'  # لون العقبات المتحركة برتقالي، الثابتة حمراء
            alpha = 0.5 if obstacle.is_dynamic else 0.7  # شفافية مختلفة لأنواع العقبات
            
            label = ""  # تهيئة نص التسمية
            # تعيين التسمية فقط للعقبة الأولى من كل نوع
            if obstacle.is_dynamic and self.dynamic_obstacles and obstacle == self.dynamic_obstacles[0]:
                label = 'Dynamic Obstacles'
            elif not obstacle.is_dynamic and self.obstacles and obstacle == self.obstacles[0]:
                label = 'Static Obstacles'
            
            plt.fill(x_coords, y_coords, color, alpha=alpha, label=label)  # رسم المضلع المعبأ
        
        # رسم مسار الروبوت
        if trail:  # إذا كانت هناك بيانات مسار
            trail_x = [p[0] for p in trail]  # استخراج إحداثيات X من مسار الروبوت
            trail_y = [p[1] for p in trail]  # استخراج إحداثيات Y من مسار الروبوت
            plt.plot(trail_x, trail_y, 'g--', linewidth=1, alpha=0.6, label='Robot Trail')  # رسم خط أخضر منقط
        
        # رسم المسارات إذا كانت متوفرة
        if chromosomes:  # إذا كانت هناك كروموسومات لعرضها
            colors = plt.cm.viridis(np.linspace(0, 1, len(chromosomes)))  # توليد ألوان متدرجة
            for i, chrom in enumerate(chromosomes):  # التكرار على الكروموسومات مع الفهرس
                if chrom.points:  # إذا كان للكروموسوم نقاط
                    x_coords = [p[0] for p in chrom.points]  # استخراج إحداثيات X
                    y_coords = [p[1] for p in chrom.points]  # استخراج إحداثيات Y
                    color = colors[i] if len(chromosomes) > 1 else 'blue'  # استخدام ألوان مختلفة إذا كان هناك أكثر من مسار
                    linestyle = '-' if chrom.is_feasible else '--'  # خط صلب إذا كان المسار ممكناً، متقطع إذا كان غير ممكن
                    # تحديد سمك الخط بناءً على اللياقة
                    linewidth = 3 if chrom == max(chromosomes, key=lambda x: x.fitness) else 1.5
                    # تحديد الشفافية بناءً على اللياقة
                    alpha = 1.0 if chrom == max(chromosomes, key=lambda x: x.fitness) else 0.6
                    
                    # رسم المسار
                    plt.plot(x_coords, y_coords, marker='o', linestyle=linestyle, 
                            color=color, alpha=alpha, linewidth=linewidth,
                            label=f'GA Path (Fit: {chrom.fitness:.4f})' if i == 0 else "")  # إضافة تسمية للمسار الأول فقط
        
        # رسم الروبوت إذا كان متوفراً
        if robot_position:  # إذا كان هناك موقع للروبوت
            robot_x, robot_y = robot_position  # فك موقع الروبوت
            # إنشاء دائرة تمثل الروبوت
            robot_circle = plt.Circle((robot_x, robot_y), 1.5, color='green', alpha=0.8, label='Robot')
            plt.gca().add_patch(robot_circle)  # إضافة الدائرة للرسم
            plt.plot(robot_x, robot_y, 'go', markersize=8, markeredgecolor='black')  # رسم نقطة مركزية للروبوت
        
        # رسم نقطتي البداية والهدف
        if self.start:
            plt.plot(self.start[0], self.start[1], 'go', markersize=15, label='Start', markeredgecolor='black')
        if self.goal:
            plt.plot(self.goal[0], self.goal[1], 'bo', markersize=15, label='Goal', markeredgecolor='black')
        
        plt.xlim(0, self.width)  # تحديد حدود المحور X
        plt.ylim(0, self.height)  # تحديد حدود المحور Y
        plt.grid(True)  # إظهار شبكة الإحداثيات
        plt.legend()  # إظهار وسيلة الإيضاح (التسميات)
        plt.title(f'{title} - Time: {self.time_step}')  # تعيين عنوان الرسم
        plt.show()  # عرض النافذة بالرسم

class Chromosome:
    def __init__(self, points):
        """تهيئة كروموسوم (مسار) جديد"""
        self.points = points  # تخزين قائمة نقاط المسار
        self.fitness = 0.0  # تهيئة قيمة اللياقة بصفر (أعلى = أفضل)
        self.total_distance = 0.0  # ستخزن مجموع أطوال جميع أجزاء المسار
        self.collision_length = 0.0  # جزء المسار الذي يمر عبر العقبات
        self.is_feasible = True  # افتراض أن المسار ممكن (غير متصادم مع عقبات)

    def calculate_distance(self, point1, point2):
        """حساب المسافة الإقليدية بين نقطتين"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)  # نظرية فيثاغورس

    def calculate_fitness(self, env, penalty_factor=1000):
        """حساب قيمة اللياقة للمسار بناء على المسافة الكلية وكمية التصادم"""
        self.total_distance = 0.0  # إعادة تعيين المسافة الكلية
        self.collision_length = 0.0  # إعادة تعيين طول التصادم
        self.is_feasible = True  # افتراض أن المسار ممكن
        
        for i in range(len(self.points) - 1):  # التكرار على جميع الأجزاء بين النقاط
            point1 = self.points[i]  # أخذ النقطة الأولى
            point2 = self.points[i + 1]  # أخذ النقطة الثانية
            
            segment_distance = self.calculate_distance(point1, point2)  # حساب مسافة هذا الجزء
            self.total_distance += segment_distance  # إضافة مسافة الجزء إلى المسافة الكلية
            
            if not env.is_line_feasible(point1, point2):  # التحقق إذا كان هذا الجزء يتصادم مع عقبة
                self.collision_length += segment_distance  # إضافة مسافة الجزء إلى طول التصادم
                self.is_feasible = False  # تغيير حالة المسار إلى "غير ممكن"
        
        # حساب التكلفة الإجمالية: المسافة الفعلية + (عقوبة التصادم × معامل العقوبة)
        total_cost = self.total_distance + (self.collision_length * penalty_factor)
        self.fitness = 1.0 / total_cost if total_cost > 0 else 0.0  # العلاقة العكسية: اللياقة = 1 ÷ التكلفة
        
        return self.fitness  # إرجاع قيمة اللياقة المحسوبة

class Robot:
    def __init__(self, start_position, environment):
        """تهيئة روبوت جديد"""
        self.position = start_position  # تخزين موقع البداية للروبوت
        self.environment = environment  # تخزين مرجع للبيئة التي يتحرك فيها الروبوت
        self.path = []  # إنشاء قائمة فارغة لتخزين المسار الذي سيتبعه الروبوت
        self.current_segment = 0  # تهيئة المؤشر للجزء الحالي من المسار (يبدأ من 0)
        self.speed = 2.0  # تحديد سرعة الروبوت (2.0 وحدة لكل خطوة)
        self.reached_goal = False  # تهيئة حالة "وصول للهدف" بـ خطأ (لم يصل بعد)
        self.distance_traveled = 0.0  # تهيئة المسافة المقطوعة بصفر
        self.trail = []  # إنشاء قائمة فارغة لتخزين مسار الروبوت الفعلي
        self.collision_detected = False  # تهيئة حالة اكتشاف التصادم بـ خطأ (لم يكتشف تصادماً)
        self.wait_counter = 0  # تهيئة عداد الانتظار بصفر (للتوقف المؤقت)
        self.avoidance_mode = False  # تهيئة وضعية تجنب العقبات بـ خطأ (ليس في وضع التجنب)
        
        # ⭐⭐ إضافة متغيرات جديدة لتحسين الأداء ⭐⭐
        self.goal_threshold = 2.0  # مسافة عتبة للوصول للهدف (بدلاً من self.speed)
        self.waypoint_threshold = 1.5  # مسافة عتبة للنقطة الوسيطة (بدلاً من self.speed)
        self.stuck_counter = 0  # عداد للتوقف (لكشف إذا كان الروبوت عالقاً)
        self.max_stuck_steps = 50  # أقصى خطوات للتوقف قبل تنفيذ استعادة
    
    def set_path(self, path_points):
        """تعيين مسار جديد للروبوت وإعادة ضبط جميع القيم"""
        self.path = path_points  # تعيين المسار الجديد (قائمة النقاط)
        self.current_segment = 0  # إعادة المؤشر لبداية المسار
        self.reached_goal = False  # إعادة تعيين حالة الوصول للهدف
        self.distance_traveled = 0.0  # إعادة تعيين المسافة المقطوعة
        self.trail = [self.position]  # بدء مسار جديد بالموقع الحالي فقط
        self.collision_detected = False  # إعادة تعيين حالة اكتشاف التصادم
        self.wait_counter = 0  # إعادة تعيين عداد الانتظار
        self.avoidance_mode = False  # إعادة تعيين وضعية تجنب العقبات
        
        # ⭐⭐ إعادة تعيين المتغيرات الجديدة ⭐⭐
        self.stuck_counter = 0  # إعادة تعيين عداد التوقف
    
    def is_collision_with_obstacles(self, new_position):
        """التحقق إذا كان الموقع الجديد يصطدم بأي عقبة مع مسافة أمان"""
        BUFFER = 0.5  # مسافة أمان حول الروبوت
        
        for obstacle in self.environment.obstacles:  # التكرار على جميع العقبات في البيئة
            # التحقق من النقطة نفسها
            if obstacle.contains_point(new_position[0], new_position[1]):
                return True  # هناك تصادم
            
            # ⭐⭐ التحقق بمسافة أمان ⭐⭐
            # تحقق من نقاط حول الموقع الجديد
            check_points = [
                (new_position[0], new_position[1]),  # النقطة المركزية
                (new_position[0] + BUFFER, new_position[1]),  # يمين
                (new_position[0] - BUFFER, new_position[1]),  # يسار
                (new_position[0], new_position[1] + BUFFER),  # أعلى
                (new_position[0], new_position[1] - BUFFER),  # أسفل
            ]
            
            for point in check_points:  # التحقق من جميع نقاط الأمان
                if obstacle.contains_point(point[0], point[1]):
                    return True  # هناك تصادم في إحدى نقاط الأمان
        
        return False  # لا يوجد تصادم
    
    def find_avoidance_direction(self, obstacle):
        """إيجاد اتجاه آمن للهروب من عقبة"""
        # حساب مركز العقبة
        center_x = sum(v[0] for v in obstacle.vertices) / len(obstacle.vertices)
        center_y = sum(v[1] for v in obstacle.vertices) / len(obstacle.vertices)
        
        # Vector from obstacle to robot
        dx = self.position[0] - center_x  # الفرق في X بين الروبوت ومركز العقبة
        dy = self.position[1] - center_y  # الفرق في Y بين الروبوت ومركز العقبة
        
        # Normalize and scale to avoidance distance
        distance = math.sqrt(dx*dx + dy*dy)  # حساب المسافة بين الروبوت ومركز العقبة
        if distance == 0:  # إذا كانت المسافة صفر (الروبوت في مركز العقبة)
            return (1, 0)  # اتجاه افتراضي (يمين)
        
        avoidance_distance = 8.0  # تحديد مسافة الهروب المطلوبة
        move_x = (dx / distance) * avoidance_distance  # تطبيع متجه الاتجاه وضربه في مسافة الهروب
        move_y = (dy / distance) * avoidance_distance
        
        return (move_x, move_y)  # إرجاع متجه الهروب
    
    def attempt_recovery(self):
        """محاولة إخراج الروبوت من حالة التوقف"""
        print(f"🆘 Attempting recovery for stuck robot at {self.position}")
        
        # قائمة بالاتجاهات المحتملة للحركة
        directions = [
            (3, 0), (-3, 0), (0, 3), (0, -3),  # الاتجاهات الأساسية
            (2, 2), (-2, 2), (2, -2), (-2, -2),  # الاتجاهات القطرية
            (4, 1), (1, 4), (-4, 1), (1, -4)  # اتجاهات إضافية
        ]
        
        for dx, dy in directions:  # تجربة جميع الاتجاهات
            new_x = self.position[0] + dx  # حساب X الجديد
            new_y = self.position[1] + dy  # حساب Y الجديد
            
            # التحقق من حدود البيئة
            new_x = max(0, min(new_x, self.environment.width))  # التأكد من أن X بين 0 وعرض البيئة
            new_y = max(0, min(new_y, self.environment.height))  # التأكد من أن Y بين 0 وارتفاع البيئة
            
            # التحقق من عدم وجود تصادم
            if not self.is_collision_with_obstacles((new_x, new_y)):
                # التحقق من أن المسار آمن
                if self.environment.is_line_feasible(self.position, (new_x, new_y)):
                    self.position = (new_x, new_y)  # تحديث موقع الروبوت
                    self.avoidance_mode = False  # الخروج من وضع التجنب
                    self.wait_counter = 0  # إعادة تعيين عداد الانتظار
                    self.stuck_counter = 0  # إعادة تعيين عداد التوقف
                    self.trail.append(self.position)  # إضافة الموقع الجديد للمسار
                    print(f"✅ Recovery successful! Moved to {self.position}")
                    return True  # نجاح الاستعادة
        
        # إذا فشلت جميع المحاولات المنظمة، حاول التحرك بشكل عشوائي
        for _ in range(10):  # 10 محاولات عشوائية
            new_x = self.position[0] + random.uniform(-5, 5)  # حركة عشوائية في X
            new_y = self.position[1] + random.uniform(-5, 5)  # حركة عشوائية في Y
            
            # التحقق من الحدود
            new_x = max(0, min(new_x, self.environment.width))
            new_y = max(0, min(new_y, self.environment.height))
            
            if not self.is_collision_with_obstacles((new_x, new_y)):  # إذا كان الموقع آمناً
                self.position = (new_x, new_y)  # تحديث الموقع
                self.trail.append(self.position)  # إضافة للمسار
                print(f"⚠️ Random recovery move to {self.position}")
                return True  # نجاح الاستعادة العشوائية
        
        print("❌ Recovery failed! Robot remains stuck.")  # فشل جميع محاولات الاستعادة
        return False  # فشل الاستعادة
    
    def move(self):
        """تحريك الروبوت خطوة واحدة"""
        if self.reached_goal:  # إذا وصل الروبوت للهدف
            return True  # ارجع صح (لا تحرك)
        
        # ⭐⭐ تحقق من التوقف ⭐⭐
        if len(self.trail) > 10:  # إذا كان هناك على الأقل 10 موقع في المسار
            recent_positions = self.trail[-10:]  # أخذ آخر 10 مواقع
            # التحقق إذا كان الروبوت في نفس المكان لـ 10 خطوات متتالية
            if all(abs(p[0] - recent_positions[0][0]) < 0.1 and 
                   abs(p[1] - recent_positions[0][1]) < 0.1 
                   for p in recent_positions):
                self.stuck_counter += 1  # زيادة عداد التوقف
                if self.stuck_counter > self.max_stuck_steps:  # إذا تجاوز العداد الحد الأقصى
                    print(f"🚨 Robot stuck at {self.position} for {self.stuck_counter} steps!")
                    if self.attempt_recovery():  # محاولة الاستعادة
                        self.stuck_counter = 0  # إعادة تعيين العداد إذا نجحت الاستعادة
                    else:
                        # إذا فشلت الاستعادة، حاول الذهاب مباشرة للهدف
                        print("🚀 Attempting direct path to goal...")
                        if self.environment.is_line_feasible(self.position, self.environment.goal):
                            self.path = [self.position, self.environment.goal]  # مسار مباشر للهدف
                            self.current_segment = 0  # إعادة تعيين المؤشر
            else:
                self.stuck_counter = 0  # إعادة تعيين العداد إذا تحرك الروبوت
        
        # If in avoidance mode, wait for a few frames
        if self.wait_counter > 0:  # إذا كان عداد الانتظار > 0
            self.wait_counter -= 1  # قلل العداد بمقدار 1
            return False  # ارجع خطأ (لا تحرك في هذه الخطوة)
        
        # Check if current position is in collision
        if self.is_collision_with_obstacles(self.position):  # إذا كان الموقع الحالي يصطدم بعقبة
            self.collision_detected = True  # سجل اكتشاف تصادم
            self.avoidance_mode = True  # انتقل لوضعية التجنب
            self.wait_counter = 10  # انتظر 10 خطوات
            print(f"🚨 COLLISION DETECTED! Robot at {self.position} is inside obstacle. Waiting...")
            return False  # لا تتحرك في هذه الخطوة
        
        if self.current_segment >= len(self.path) - 1:  # إذا انتهى الروبوت من جميع أجزاء المسار
            # Moving to final goal
            current_point = self.position  # أخذ الموقع الحالي للروبوت
            goal_point = self.environment.goal  # أخذ موقع الهدف من البيئة
            
            # Check if direct path to goal is safe
            if not self.environment.is_line_feasible(current_point, goal_point):  # إذا كان الخط المباشر للهدف غير آمن
                self.avoidance_mode = True  # انتقل لوضعية التجنب
                self.wait_counter = 5  # انتظر 5 خطوات
                return False  # لا تتحرك في هذه الخطوة
            
            dx = goal_point[0] - current_point[0]  # حساب الفرق في X بين الهدف والموقع الحالي
            dy = goal_point[1] - current_point[1]  # حساب الفرق في Y بين الهدف والموقع الحالي
            distance = math.sqrt(dx**2 + dy**2)  # حساب المسافة للهدف
            
            # ⭐⭐ استبدال شرط الوصول للهدف ⭐⭐
            if distance < self.goal_threshold:  # إذا كانت المسافة أقل من عتبة الوصول للهدف
                self.position = goal_point  # ضع الروبوت مباشرة على الهدف
                self.reached_goal = True  # سجل الوصول للهدف
                self.trail.append(self.position)  # أضف الهدف للمسار المقطوع
                print(f"🎯 Goal reached! Final position: {self.position}")
                return True  # الوصول للهدف
            
            move_distance = min(self.speed, distance)  # تحديد مسافة الحركة (أيهما أقل)
            ratio = move_distance / distance  # حساب نسبة الحركة
            
            new_x = current_point[0] + dx * ratio  # حساب الإحداثي X الجديد
            new_y = current_point[1] + dy * ratio  # حساب الإحداثي Y الجديد
            
            # Check if new position is safe
            if not self.is_collision_with_obstacles((new_x, new_y)):  # إذا كان الموقع الجديد آمناً
                self.position = (new_x, new_y)  # تحديث موقع الروبوت
                self.trail.append(self.position)  # أضف الموقع الجديد للمسار المقطوع
                self.distance_traveled += move_distance  # أضف مسافة الحركة للمسافة الكلية
                self.avoidance_mode = False  # خرج من وضعية التجنب
            else:
                self.avoidance_mode = True  # ادخل وضعية التجنب
                self.wait_counter = 5  # انتظر 5 خطوات
            
            return False  # لم يصل للهدف بعد
        
        # Normal movement between path points
        current_point = self.path[self.current_segment]  # أخذ النقطة الحالية من المسار
        next_point = self.path[self.current_segment + 1]  # أخذ النقطة التالية من المسار
        
        # حساب المسافة بين الروبوت والنقطة الحالية من المسار
        dist_to_current = math.sqrt((self.position[0]-current_point[0])**2 + 
                                  (self.position[1]-current_point[1])**2)
        
        # ⭐⭐ تعديل شرط الانتقال بين النقاط ⭐⭐
        if dist_to_current > self.waypoint_threshold:  # إذا كانت المسافة أكبر من عتبة النقطة الوسيطة
            # Move towards current waypoint
            dx = current_point[0] - self.position[0]  # حساب الفرق في X بين النقطة الحالية والروبوت
            dy = current_point[1] - self.position[1]  # حساب الفرق في Y بين النقطة الحالية والروبوت
            distance = math.sqrt(dx**2 + dy**2)  # حساب المسافة الكلية
            
            move_distance = min(self.speed, distance)  # تحديد مسافة الحركة
            ratio = move_distance / distance  # حساب نسبة الحركة
            
            new_x = self.position[0] + dx * ratio  # حساب X الجديد
            new_y = self.position[1] + dy * ratio  # حساب Y الجديد
            
            # Check if new position is safe and path is feasible
            if (not self.is_collision_with_obstacles((new_x, new_y)) and 
                self.environment.is_line_feasible(self.position, (new_x, new_y))):  # إذا كان الموقع الجديد آمناً والخط ممكناً
                self.position = (new_x, new_y)  # تحديث الموقع
                self.trail.append(self.position)  # أضف للمسار المقطوع
                self.distance_traveled += move_distance  # أضف المسافة
                self.avoidance_mode = False  # خرج من وضعية التجنب

            else:
                # Find nearest obstacle and avoid it
                nearest_obstacle = None  # تهيئة متغير لأقرب عقبة
                min_distance = float('inf')  # قيمة أولية لا نهائية للمسافة
                
                for obstacle in self.environment.obstacles:  # التكرار على جميع العقبات
                    if obstacle.is_dynamic:  # فقط العقبات المتحركة
                        # حساب مركز العقبة
                        center_x = sum(v[0] for v in obstacle.vertices) / len(obstacle.vertices)
                        center_y = sum(v[1] for v in obstacle.vertices) / len(obstacle.vertices)
                        # حساب المسافة بين الروبوت ومركز العقبة
                        dist = math.sqrt((self.position[0]-center_x)**2 + (self.position[1]-center_y)**2)
                        if dist < min_distance:  # إذا كانت هذه العقبة أقرب
                            min_distance = dist  # تحديث أقرب مسافة
                            nearest_obstacle = obstacle  # تحديث أقرب عقبة
                
                if nearest_obstacle:  # إذا وجدت عقبة قريبة
                    avoid_dx, avoid_dy = self.find_avoidance_direction(nearest_obstacle)  # احسب اتجاه الهروب
                    new_x = self.position[0] + avoid_dx * 0.5  # حساب موقع جديد باتجاه الهروب (نصف المسافة)
                    new_y = self.position[1] + avoid_dy * 0.5
                    
                    # Ensure new position is within bounds and safe
                    new_x = max(0, min(new_x, self.environment.width))  # التأكد أن X الجديد ضمن الحدود
                    new_y = max(0, min(new_y, self.environment.height))  # التأكد أن Y الجديد ضمن الحدود
                    
                    if not self.is_collision_with_obstacles((new_x, new_y)):  # إذا كان الموقع الجديد آمناً
                        self.position = (new_x, new_y)  # تحديث موقع الروبوت
                        self.trail.append(self.position)  # أضف للمسار المقطوع
                        # أضف المسافة المقطوعة (نصف مسافة الهروب)
                        self.distance_traveled += math.sqrt(avoid_dx**2 + avoid_dy**2) * 0.5
                        self.avoidance_mode = True  # ادخل وضعية التجنب
                        print(f"🔄 AVOIDING obstacle at position {self.position}")
        else:
            self.current_segment += 1  # انتقل للنقطة التالية في المسار
            print(f"📍 Reached waypoint {self.current_segment-1}, moving to next")
        return False  # لم يصل للهدف بعد

class DynamicGeneticAlgorithm:
    def __init__(self, env, population_size=40, crossover_prob=0.75, mutation_prob=0.3, 
                 elitism_count=2, tournament_size=3, memory_size=10, random_immigrants_ratio=0.2):
        """تهيئة خوارزمية جينية ديناميكية
        
        المعاملات:
        env: بيئة المحاكاة
        population_size: حجم المجتمع (عدد المسارات)
        crossover_prob: احتمال التكاثر (75%)
        mutation_prob: احتمال الطفرة (30%)
        elitism_count: عدد النخبة (أفضل المسارات التي تنتقل للأجيال التالية مباشرة)
        tournament_size: حجم البطولة (لاختيار الوالدين)
        memory_size: حجم الذاكرة (لتخزين أفضل الحلول السابقة)
        random_immigrants_ratio: نسبة المهاجرين العشوائيين (20%)
        """
        self.env = env  # البيئة
        self.population_size = population_size  # حجم المجتمع
        self.crossover_prob = crossover_prob  # احتمال التكاثر
        self.mutation_prob = mutation_prob  # احتمال الطفرة
        self.elitism_count = elitism_count  # عدد النخبة
        self.tournament_size = tournament_size  # حجم البطولة
        self.memory_size = memory_size  # حجم الذاكرة
        self.random_immigrants_ratio = random_immigrants_ratio  # نسبة المهاجرين
        
        self.population = []  # المجتمع الحالي (قائمة من الكروموسومات)
        self.memory = []  # ذاكرة الحلول السابقة
        self.generation = 0  # عدد الأجيال
        self.best_fitness_history = []  # تاريخ أفضل لياقة
        self.average_fitness_history = []  # تاريخ متوسط اللياقة
        self.environment_changes = 0  # عدد التغيرات في البيئة
        
    def initialize_population(self):
        """إنشاء المجتمع الأولي من المسارات العشوائية"""
        self.population = []  # إعادة تعيين المجتمع
        
        # إنشاء نصف المجتمع عشوائياً
        for _ in range(self.population_size // 2):  # عدد التكرارات = نصف حجم المجتمع
            num_points = random.randint(3, 7)  # عدد نقاط عشوائي بين 3 و 7
            self.population.append(self.generate_random_chromosome(num_points))  # إضافة كروموسوم عشوائي
        
        # إكمال المجتمع بالتكاثر
        for _ in range(self.population_size - len(self.population)):  # حتى يكتمل حجم المجتمع
            if len(self.population) >= 2:  # إذا كان هناك على الأقل كروموسومان
                parent1, parent2 = random.sample(self.population, 2)  # اختيار والدين عشوائيين
                child = self.one_point_crossover(parent1, parent2)[0]  # تكاثر لإنتاج طفل
                self.population.append(child)  # إضافة الطفل للمجتمع
            else:
                num_points = random.randint(3, 7)  # عدد نقاط عشوائي
                self.population.append(self.generate_random_chromosome(num_points))  # إضافة كروموسوم عشوائي
        
        self.evaluate_population()  # تقييم لياقة جميع المسارات في المجتمع
    
    def generate_random_point(self):
        """توليد نقطة عشوائية آمنة (لا تصطدم بعقبة)"""
        while True:  # حلقة لا نهائية حتى تجد نقطة آمنة
            x = random.randint(0, self.env.width)  # توليد إحداثي X عشوائي بين 0 وعرض البيئة
            y = random.randint(0, self.env.height)  # توليد إحداثي Y عشوائي بين 0 وارتفاع البيئة
            if self.env.is_point_feasible(x, y):  # إذا كانت النقطة آمنة
                return (x, y)  # أرجع الإحداثيات
    
    def generate_random_chromosome(self, num_points=5):
        """إنشاء كروموسوم (مسار) عشوائي"""
        points = [self.env.start]  # بدء المسار بنقطة البداية
        for _ in range(num_points):  # إضافة عدد محدد من النقاط العشوائية
            points.append(self.generate_random_point())  # إضافة نقطة عشوائية آمنة
        points.append(self.env.goal)  # إنهاء المسار بنقطة الهدف
        return Chromosome(points)  # إنشاء كائن كروموسوم وإرجاعه
    
    def evaluate_population(self):
        """حساب لياقة جميع الكروموسومات في المجتمع"""
        for chrom in self.population:  # التكرار على جميع الكروموسومات في المجتمع
            chrom.calculate_fitness(self.env)  # حساب اللياقة لكل كروموسوم
    
    def update_memory(self):
        """تحديث ذاكرة الحلول الجيدة السابقة"""
        sorted_pop = sorted(self.population, key=lambda x: x.fitness, reverse=True)  # ترتيب المجتمع تنازلياً حسب اللياقة
        
        for chrom in sorted_pop[:self.elitism_count]:  # التكرار على أفضل الكروموسومات (النخبة)
            if len(self.memory) < self.memory_size:  # إذا الذاكرة ليست ممتلئة
                self.memory.append(copy.deepcopy(chrom))  # أضف نسخة من الكروموسوم
            else:
                worst_in_memory = min(self.memory, key=lambda x: x.fitness)  # إيجاد أسوأ حل في الذاكرة
                if chrom.fitness > worst_in_memory.fitness:  # إذا كان الحل الجديد أفضل
                    self.memory.remove(worst_in_memory)  # احذف الأسوأ
                    self.memory.append(copy.deepcopy(chrom))  # أضف الجديد
        
        self.memory.sort(key=lambda x: x.fitness, reverse=True)  # ترتيب الذاكرة تنازلياً
        self.memory = self.memory[:self.memory_size]  # احتفظ فقط بأفضل memory_size حل
    
    def apply_memory_with_random_immigrants(self):
        """تطبيق تقنية MRI (ذاكرة + مهاجرين عشوائيين) عند تغير البيئة"""
        new_population = []  # إنشاء مجتمع جديد فارغ
        
        memory_count = min(len(self.memory), self.population_size // 3)  # حساب عدد الحلول من الذاكرة
        for i in range(memory_count):  # التكرار على أفضل الحلول في الذاكرة
            memory_chrom = copy.deepcopy(self.memory[i])  # نسخ كروموسوم من الذاكرة
            memory_chrom.points[0] = self.env.start  # تحديث نقطة البداية
            memory_chrom.points[-1] = self.env.goal  # تحديث نقطة الهدف
            memory_chrom.calculate_fitness(self.env)  # إعادة التقييم في البيئة الجديدة
            new_population.append(memory_chrom)  # إضافة للمجتمع الجديد
        
        immigrant_count = int(self.population_size * self.random_immigrants_ratio)  # حساب عدد المهاجرين العشوائيين
        for _ in range(immigrant_count):  # إضافة المهاجرين
            new_population.append(self.generate_random_chromosome(random.randint(3, 7)))  # إضافة كروموسوم عشوائي
        
        remaining_count = self.population_size - len(new_population)  # حساب العدد المتبقي لإكمال المجتمع
        if remaining_count > 0:  # إذا كان هناك مكان متبقي
            sorted_current = sorted(self.population, key=lambda x: x.fitness, reverse=True)  # ترتيب المجتمع الحالي
            for i in range(min(remaining_count, len(sorted_current))):  # إضافة أفضل الحلول الحالية
                adapted_chrom = copy.deepcopy(sorted_current[i])  # نسخ الكروموسوم
                adapted_chrom.points[0] = self.env.start  # تحديث البداية
                adapted_chrom.points[-1] = self.env.goal  # تحديث الهدف
                adapted_chrom.calculate_fitness(self.env)  # إعادة التقييم
                new_population.append(adapted_chrom)  # إضافة للمجتمع الجديد
        
        self.population = new_population  # تعيين المجتمع الجديد
        self.environment_changes += 1  # زيادة عداد تغيرات البيئة
        print(f"Environment change detected! Applied MRI technique. Change #{self.environment_changes}")
    
    def detect_environment_change(self):
        """كشف إذا تغيرت البيئة (أضيفت عقبة، تغير الهدف، إلخ)"""
        if not self.population:  # إذا المجتمع فارغ
            return False  # لا يوجد تغيير
        
        best_chrom = max(self.population, key=lambda x: x.fitness)  # إيجاد أفضل كروموسوم في المجتمع
        current_fitness = best_chrom.calculate_fitness(self.env)  # إعادة حساب لياقته في البيئة الحالية
        
        # إذا كان المسار غير ممكن أو لياقته الجديدة أقل من 50% من لياقته القديمة
        if not best_chrom.is_feasible or current_fitness < best_chrom.fitness * 0.5:
            return True  # هناك تغيير في البيئة
        
        return False  # لا يوجد تغيير
    
    def elitist_selection(self):
        """اختيار أفضل الكروموسومات مباشرة (النخبة)"""
        sorted_pop = sorted(self.population, key=lambda x: x.fitness, reverse=True)  # ترتيب المجتمع تنازلياً
        return sorted_pop[:self.elitism_count]  # إرجاع أول elitism_count كروموسومات (الأفضل)
    
    def tournament_selection(self):
        """اختيار والد بطريقة البطولة"""
        tournament = random.sample(self.population, self.tournament_size)  # اختيار عشوائي لـ tournament_size كروموسومات
        return max(tournament, key=lambda x: x.fitness)  # إرجاع الكروموسوم ذو اللياقة الأعلى
    
    def one_point_crossover(self, parent1, parent2):
        """تكاثر نقطة واحدة (تقليدية)"""
        if len(parent1.points) < 3 or len(parent2.points) < 3:  # إذا كان أي والد قصير جداً
            return parent1, parent2  # أرجع الوالدين كما هما
        
        crossover_point1 = random.randint(1, len(parent1.points) - 2)  # اختيار نقطة تقاطع عشوائية للوالد 1
        crossover_point2 = random.randint(1, len(parent2.points) - 2)  # اختيار نقطة تقاطع عشوائية للوالد 2
        
        child1_points = parent1.points[:crossover_point1] + parent2.points[crossover_point2:]  # إنشاء الطفل الأول
        child2_points = parent2.points[:crossover_point2] + parent1.points[crossover_point1:]  # إنشاء الطفل الثاني
        
        child1_points[0] = self.env.start  # ضمان البداية الصحيحة للطفل 1
        child1_points[-1] = self.env.goal  # ضمان الهدف الصحيح للطفل 1
        child2_points[0] = self.env.start  # ضمان البداية الصحيحة للطفل 2
        child2_points[-1] = self.env.goal  # ضمان الهدف الصحيح للطفل 2
        
        return Chromosome(child1_points), Chromosome(child2_points)  # إرجاع الطفلين
    
    def intelligent_crossover(self, parent1, parent2):
        """تكاثر ذكي يختار أفضل النقاط من كلا الوالدين"""
        child_points = [self.env.start]  # بدء المسار بنقطة البداية
        current_point = self.env.start  # النقطة الحالية (تبدأ من البداية)
        
        max_iterations = 20  # أقصى عدد محاولات (لضمان عدم التوقف اللانهائي)
        iteration = 0  # عداد المحاولات
        
        while current_point != self.env.goal and iteration < max_iterations:  # كرر حتى الوصول للهدف أو انتهاء المحاولات
            iteration += 1  # زيادة عداد المحاولات
            
            idx1 = self.find_point_index(parent1.points, current_point)  # إيجاد موقع النقطة الحالية في الوالد 1
            idx2 = self.find_point_index(parent2.points, current_point)  # إيجاد موقع النقطة الحالية في الوالد 2
            
            if idx1 == -1 and idx2 == -1:  # إذا لم توجد النقطة في أي والد
                break  # توقف
            
            next_points = []  # قائمة بالنقاط التالية المحتملة
            if idx1 != -1 and idx1 + 1 < len(parent1.points):  # إذا كانت هناك نقطة تالية في الوالد 1
                next_points.append(parent1.points[idx1 + 1])  # إضافة النقطة التالية من الوالد 1
            if idx2 != -1 and idx2 + 1 < len(parent2.points):  # إذا كانت هناك نقطة تالية في الوالد 2
                next_points.append(parent2.points[idx2 + 1])  # إضافة النقطة التالية من الوالد 2
            
            if not next_points:  # إذا لم توجد نقاط تالية
                break  # توقف
            
            best_point = None  # تهيئة أفضل نقطة
            best_score = float('inf')  # أفضل درجة (تبدأ بقيمة لا نهائية)
            
            for point in next_points:  # التقييم على جميع النقاط التالية المحتملة
                is_feasible = self.env.is_line_feasible(current_point, point)  # هل الخط ممكن؟
                distance_to_goal = self.calculate_distance(point, self.env.goal)  # المسافة للهدف
                
                score = distance_to_goal  # الدرجة = المسافة للهدف
                if not is_feasible:  # إذا كان الخط مستحيلاً
                    score += 1000  # أضف عقوبة كبيرة
                
                if score < best_score:  # إذا كانت هذه النقطة أفضل
                    best_score = score  # تحديث أفضل درجة
                    best_point = point  # تحديث أفضل نقطة
            
            if best_point is None and next_points:  # إذا لم يُختَر أي نقطة
                best_point = next_points[0]  # خذ أول نقطة
            
            child_points.append(best_point)  # إضافة أفضل نقطة للمسار الجديد
            current_point = best_point  # تحديث النقطة الحالية
        
        if child_points[-1] != self.env.goal:  # إذا لم تكن آخر نقطة هي الهدف
            child_points.append(self.env.goal)  # إضافة نقطة الهدف
        
        return Chromosome(child_points)  # إرجاع الكروموسوم الجديد
    
    def find_point_index(self, points, target_point):
        """إيجاد فهرس نقطة في قائمة"""
        for i, point in enumerate(points):  # التكرار على النقاط مع الفهرس
            if point == target_point:  # إذا وجدت النقطة
                return i  # أرجع الفهرس
        return -1  # إذا لم توجد النقطة
    
    def calculate_distance(self, point1, point2):
        """حساب المسافة بين نقطتين (نظرية فيثاغورس)"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def mutate(self, chromosome):
        """تطبيق طفرة على كروموسوم"""
        mutated = copy.deepcopy(chromosome)  # نسخ الكروموسوم
        
        if random.random() < self.mutation_prob:  # إذا كان الرقم العشوائي أقل من احتمال الطفرة (30%)
            mutation_type = random.choice(['add', 'delete', 'change', 'shorten', 'correct'])  # اختيار نوع طفرة عشوائياً
            
            if mutation_type == 'add' and len(mutated.points) < 15:  # إذا كان النوع "إضافة" وهناك مساحة
                self.add_node_mutation(mutated)  # تطبيق طفرة إضافة عقدة
            elif mutation_type == 'delete' and len(mutated.points) > 3:  # إذا كان النوع "حذف" وهناك نقاط كافية
                self.delete_node_mutation(mutated)  # تطبيق طفرة حذف عقدة
            elif mutation_type == 'change':  # إذا كان النوع "تغيير"
                self.change_node_mutation(mutated)  # تطبيق طفرة تغيير عقدة
            elif mutation_type == 'shorten' and len(mutated.points) > 3:  # إذا كان النوع "تقصير" وهناك نقاط كافية
                self.shorten_path_mutation(mutated)  # تطبيق طفرة تقصير المسار
            elif mutation_type == 'correct':  # إذا كان النوع "تصحيح"
                self.correct_path_mutation(mutated)  # تطبيق طفرة تصحيح المسار
        
        mutated.calculate_fitness(self.env)  # إعادة حساب اللياقة بعد الطفرة
        return mutated  # إرجاع الكروموسوم المتحور
    
    def add_node_mutation(self, chromosome):
        """طفرة إضافة عقدة جديدة"""
        if len(chromosome.points) >= 2:  # إذا كان هناك على الأقل نقطتان
            idx = random.randint(1, len(chromosome.points) - 1)  # اختيار موقع عشوائي للإضافة
            new_point = self.generate_random_point()  # توليد نقطة عشوائية
            chromosome.points.insert(idx, new_point)  # إدخال النقطة الجديدة
    
    def delete_node_mutation(self, chromosome):
        """طفرة حذف عقدة"""
        if len(chromosome.points) > 3:  # إذا كان هناك أكثر من 3 نقاط
            idx = random.randint(1, len(chromosome.points) - 2)  # اختيار موقع عشوائي للحذف
            chromosome.points.pop(idx)  # حذف النقطة
    
    def change_node_mutation(self, chromosome):
        """طفرة تغيير عقدة"""
        if len(chromosome.points) > 2:  # إذا كان هناك أكثر من نقطتين
            idx = random.randint(1, len(chromosome.points) - 2)  # اختيار موقع عشوائي للتغيير
            new_point = self.generate_random_point()  # توليد نقطة عشوائية
            chromosome.points[idx] = new_point  # استبدال النقطة القديمة بالجديدة
    
    def shorten_path_mutation(self, chromosome):
        """طفرة تقصير المسار بإزالة النقاط غير الضرورية"""
        if len(chromosome.points) <= 3:  # إذا كان المسار قصيراً جداً
            return  # لا تفعل شيئاً
        
        points_to_remove = []  # قائمة بالنقاط المراد حذفها
        for i in range(1, len(chromosome.points) - 2):  # التكرار على النقاط الداخلية
            point_before = chromosome.points[i-1]  # النقطة السابقة
            point_after = chromosome.points[i+1]  # النقطة التالية
            
            if self.env.is_line_feasible(point_before, point_after):  # إذا كان الخط بين النقطة السابقة واللاحقة ممكناً
                points_to_remove.append(i)  # أضف الفهرس لقائمة الحذف
        
        for idx in sorted(points_to_remove, reverse=True):  # حذف النقاط من الأخير للأول
            if len(chromosome.points) > 3:  # إذا كان هناك أكثر من 3 نقاط
                chromosome.points.pop(idx)  # حذف النقطة
    
    def correct_path_mutation(self, chromosome):
        """طفرة تصحيح المسار بإضافة نقاط وسيطة عند التصادم"""
        if chromosome.is_feasible:  # إذا كان المسار ممكناً بالفعل
            return  # لا تفعل شيئاً
        
        new_points = [self.env.start]  # بدء مسار جديد بنقطة البداية
        
        for i in range(len(chromosome.points) - 1):  # التكرار على أجزاء المسار
            current_point = chromosome.points[i]  # النقطة الحالية
            next_point = chromosome.points[i + 1]  # النقطة التالية
            
            if not self.env.is_line_feasible(current_point, next_point):  # إذا كان الجزء غير ممكن
                mid_point = self.find_feasible_midpoint(current_point, next_point)  # إيجاد نقطة وسيطة آمنة
                if mid_point:  # إذا وجدت نقطة وسيطة
                    new_points.append(mid_point)  # إضافة النقطة الوسيطة
            new_points.append(next_point)  # إضافة النقطة التالية
        
        unique_points = []  # قائمة للنقاط الفريدة
        for point in new_points:  # التكرار على جميع النقاط
            if point not in unique_points:  # إذا كانت النقطة غير موجودة في القائمة
                unique_points.append(point)  # إضافتها
        
        chromosome.points = unique_points  # تحديث نقاط الكروموسوم
    
    def find_feasible_midpoint(self, point1, point2):
        """إيجاد نقطة وسطية آمنة بين نقطتين"""
        mid_x = (point1[0] + point2[0]) // 2  # حساب منتصف X
        mid_y = (point1[1] + point2[1]) // 2  # حساب منتصف Y
        
        if self.env.is_point_feasible(mid_x, mid_y):  # إذا كانت نقطة المنتصف آمنة
            return (mid_x, mid_y)  # أرجعها
        
        for _ in range(10):  # 10 محاولات للعثور على نقطة قريبة آمنة
            offset_x = random.randint(-10, 10)  # إزاحة عشوائية في X
            offset_y = random.randint(-10, 10)  # إزاحة عشوائية في Y
            new_x = mid_x + offset_x  # حساب X الجديد
            new_y = mid_y + offset_y  # حساب Y الجديد
            
            if self.env.is_point_feasible(new_x, new_y):  # إذا كانت النقطة الجديدة آمنة
                return (new_x, new_y)  # أرجعها
        
        return None  # إذا فشلت جميع المحاولات
    
    def run_generation(self):
        """تنفيذ جيل واحد من الخوارزمية الجينية"""
        if self.detect_environment_change():  # كشف التغيرات في البيئة
            self.apply_memory_with_random_immigrants()  # تطبيق تقنية MRI
        
        new_population = []  # إنشاء مجتمع جديد فارغ
        
        elites = self.elitist_selection()  # اختيار النخبة
        new_population.extend(elites)  # إضافتها للمجتمع الجديد
        
        while len(new_population) < self.population_size:  # حتى يكتمل حجم المجتمع
            parent1 = self.tournament_selection()  # اختيار الوالد الأول
            parent2 = self.tournament_selection()  # اختيار الوالد الثاني
            
            if random.random() < self.crossover_prob:  # 75% احتمال للتكاثر
                child = self.intelligent_crossover(parent1, parent2)  # تكاثر ذكي
                new_population.append(child)  # إضافة الطفل للمجتمع الجديد
            else:
                if len(new_population) < self.population_size:  # إذا كان هناك مكان
                    new_population.append(copy.deepcopy(parent1))  # إضافة نسخة من الوالد
        
        for i in range(len(new_population)):  # التكرار على المجتمع الجديد
            if i >= self.elitism_count:  # إذا لم يكن من النخبة
                new_population[i] = self.mutate(new_population[i])  # تطبيق الطفرة
        
        self.population = new_population  # تحديث المجتمع
        self.evaluate_population()  # تقييم المجتمع الجديد
        
        self.update_memory()  # تحديث الذاكرة
        
        self.generation += 1  # زيادة عداد الأجيال
        
        self.record_statistics()  # تسجيل الإحصائيات
    
    def record_statistics(self):
        """تسجيل إحصائيات الجيل الحالي"""
        fitnesses = [chrom.fitness for chrom in self.population]  # استخراج قيم اللياقة
        self.best_fitness_history.append(max(fitnesses) if fitnesses else 0)  # إضافة أفضل لياقة للتاريخ
        self.average_fitness_history.append(sum(fitnesses) / len(fitnesses) if fitnesses else 0)  # إضافة متوسط اللياقة
    
    def evolve(self, generations=100, dynamic_events=None):
        """تنفيذ الخوارزمية لعدد محدد من الأجيال"""
        print(f"Starting dynamic evolution for {generations} generations...")  # رسالة بدء
        
        if dynamic_events is None:  # إذا لم يتم توفير أحداث ديناميكية
            dynamic_events = []  # قائمة فارغة
        
        event_index = 0  # مؤشر للأحداث
        
        for gen in range(generations):  # التكرار على الأجيال
            if event_index < len(dynamic_events) and gen >= dynamic_events[event_index]['generation']:  # إذا كان هناك حدث في هذا الجيل
                event = dynamic_events[event_index]  # أخذ الحدث الحالي
                self.trigger_dynamic_event(event)  # تنفيذ الحدث
                event_index += 1  # زيادة مؤشر الأحداث
            
            self.env.update_dynamic_obstacles()  # تحديث العقبات المتحركة
            
            self.run_generation()  # تنفيذ جيل واحد
            
            if gen % 10 == 0:  # كل 10 أجيال
                stats = self.get_statistics()  # الحصول على الإحصائيات
                print(f"Generation {gen}: Best fitness = {stats['best_fitness']:.6f}, "  # طباعة الإحصائيات
                      f"Best distance = {stats['best_distance']:.2f}")
        
        print("Dynamic evolution completed!")  # رسالة انتهاء
    
    def trigger_dynamic_event(self, event):
        """تنفيذ حدث ديناميكي (إضافة عقبة، تغيير هدف)"""
        event_type = event['type']  # نوع الحدث
        
        if event_type == 'add_obstacle':  # إذا كان الحدث إضافة عقبة
            self.env.add_random_obstacle(size=event.get('size', 5),  # إضافة عقبة عشوائية
                                       is_dynamic=event.get('dynamic', False))
            print(f"Dynamic event: Added new obstacle at generation {self.generation}")  # رسالة
        
        elif event_type == 'change_goal':  # إذا كان الحدث تغيير الهدف
            if event.get('new_goal'):  # إذا كان هناك هدف جديد
                new_goal = event['new_goal']  # أخذ الهدف الجديد
                self.env.goal = new_goal  # تحديث الهدف
                print(f"Dynamic event: Goal changed to {self.env.goal} at generation {self.generation}")  # رسالة
    
    def get_best_chromosome(self):
        """الحصول على أفضل كروموسوم في المجتمع"""
        if not self.population:  # إذا كان المجتمع فارغاً
            return None  # أرجع None
        return max(self.population, key=lambda x: x.fitness)  # إرجاع الكروموسوم بأعلى لياقة
    
    def get_statistics(self):
        """جمع إحصائيات المجتمع الحالي"""
        if not self.population:  # إذا كان المجتمع فارغاً
            return {}  # أرجع قاموساً فارغاً
        
        fitnesses = [chrom.fitness for chrom in self.population]  # قيم اللياقة
        distances = [chrom.total_distance for chrom in self.population]  # المسافات
        feasible_count = sum(1 for chrom in self.population if chrom.is_feasible)  # عدد المسارات الممكنة
        
        return {
            'best_fitness': max(fitnesses),  # أفضل لياقة
            'worst_fitness': min(fitnesses),  # أسوأ لياقة
            'average_fitness': sum(fitnesses) / len(fitnesses),  # متوسط اللياقة
            'best_distance': min(distances),  # أفضل مسافة (أقصر)
            'worst_distance': max(distances),  # أسوأ مسافة (أطول)
            'average_distance': sum(distances) / len(distances),  # متوسط المسافة
            'feasible_ratio': feasible_count / len(self.population),  # نسبة المسارات الممكنة
            'generation': self.generation,  # رقم الجيل
            'environment_changes': self.environment_changes,  # عدد تغيرات البيئة
            'memory_size': len(self.memory)  # حجم الذاكرة
        }

class MatplotlibAnimation:
    def __init__(self, env, robot, best_path):
        """تهيئة رسوم متحركة باستخدام Matplotlib"""
        self.env = env  # البيئة
        self.robot = robot  # الروبوت
        self.best_path = best_path  # أفضل مسار
        self.fig = None  # تهيئة متغير النافذة الرسومية
        self.ax = None  # تهيئة متغير المحاور
        self.animation = None  # تهيئة متغير الرسوم المتحركة
        
    def simulate_movement(self):
        """بدء وتشغيل المحاكاة المرئية للروبوت"""
        print("\n Starting LIVE robot animation with Matplotlib...")  # رسالة بدء
        self.robot.set_path(self.best_path.points)  # تعيين أفضل مسار للروبوت
        
        required_steps = self.calculate_required_steps()  # حساب عدد الخطوات المطلوبة
        print(f" Estimated steps to reach goal: {required_steps}")  # طباعة عدد الخطوات
        
        self.fig, self.ax = plt.subplots(figsize=(12, 10))  # إنشاء نافذة رسم جديدة
        
        self.animation = FuncAnimation(  # إنشاء رسوم متحركة
            self.fig, 
            self.animate,  # دالة الرسم لكل إطار
            frames=required_steps + 100,  # عدد الإطارات (الخطوات + 100 احتياطي)
            interval=100,  # الفترة بين الإطارات (100 مللي ثانية)
            repeat=False,  # عدم التكرار
            blit=False  # لا تستخدم تقنية blit (للرسوم المعقدة)
        )
        
        print(" Animation started! Close the window to stop.")  # رسالة
        plt.show()  # عرض النافذة
        
        if self.robot.reached_goal:  # إذا وصل الروبوت للهدف
            print(f" Robot reached goal!")  # رسالة
            print(f" Total distance traveled: {self.robot.distance_traveled:.2f}")  # المسافة المقطوعة
            print(f" Optimal path length: {self.best_path.total_distance:.2f}")  # طول المسار الأمثل
        else:
            print(f"Robot did not reach goal within animation frames")  # رسالة
        
        print(" Animation completed!")  # رسالة انتهاء
    
    def animate(self, frame):
        """رسم إطار واحد من الرسوم المتحركة"""
        self.ax.clear()  # مسح الرسم السابق من المحاور
        
        for obstacle in self.env.obstacles:  # رسم العقبات
            vertices = obstacle.vertices  # إحداثيات العقبة
            x_coords = [v[0] for v in vertices] + [vertices[0][0]]  # إحداثيات X مع إغلاق المضلع
            y_coords = [v[1] for v in vertices] + [vertices[0][1]]  # إحداثيات Y مع إغلاق المضلع
            
            color = 'orange' if obstacle.is_dynamic else 'red'  # لون العقبات المتحركة برتقالي
            alpha = 0.6 if obstacle.is_dynamic else 0.7  # شفافية
            label = "Dynamic Obstacles" if obstacle.is_dynamic else "Static Obstacles"  # تسمية
            self.ax.fill(x_coords, y_coords, color, alpha=alpha, label=label)  # رسم المضلع المعبأ
            
            # Add velocity indicator for dynamic obstacles
            if obstacle.is_dynamic:  # إذا كانت العقبة متحركة
                center_x = sum(v[0] for v in vertices) / len(vertices)  # مركز X
                center_y = sum(v[1] for v in vertices) / len(vertices)  # مركز Y
                dx, dy = obstacle.velocity  # السرعة
                if dx != 0 or dy != 0:  # إذا كانت تتحرك
                    # رسم سهم يوضح اتجاه الحركة
                    self.ax.arrow(center_x, center_y, dx*3, dy*3, head_width=2, 
                                head_length=1, fc='yellow', ec='yellow', alpha=0.8)
        
        if self.best_path.points:  # إذا كان هناك مسار أمثل
            x_coords = [p[0] for p in self.best_path.points]  # إحداثيات X للمسار
            y_coords = [p[1] for p in self.best_path.points]  # إحداثيات Y للمسار
            self.ax.plot(x_coords, y_coords, 'b-', linewidth=3, label='GA Optimized Path', alpha=0.8)  # رسم المسار
            self.ax.plot(x_coords, y_coords, 'bo', markersize=6, alpha=0.7)  # رسم نقاط المسار
        
        if self.robot.trail:  # إذا كان هناك مسار للروبوت
            trail_x = [p[0] for p in self.robot.trail]  # إحداثيات X للمسار
            trail_y = [p[1] for p in self.robot.trail]  # إحداثيات Y للمسار
            self.ax.plot(trail_x, trail_y, 'g-', linewidth=2, alpha=0.8, label='Robot Trail')  # رسم مسار الروبوت
        
        # ⭐⭐ تحسين لون الروبوت للإشارة لحالة التوقف ⭐⭐
        robot_color = 'red' if self.robot.collision_detected else 'lime'  # أحمر إذا اصطدم، أخضر إذا سليم
        if self.robot.stuck_counter > 10:  # إذا كان الروبوت عالقاً
            robot_color = 'purple'  # لون أرجواني للإشارة للتوقف
        
        robot_circle = plt.Circle(self.robot.position, 2.5, color=robot_color, alpha=0.9,  # رسم الروبوت كدائرة
                                label='Robot', edgecolor='darkgreen', linewidth=2)
        self.ax.add_patch(robot_circle)  # إضافة الدائرة للرسم
        
        if len(self.robot.trail) > 1:  # إذا كان هناك موقع سابق
            prev_pos = self.robot.trail[-2]  # الموقع السابق
            dx = self.robot.position[0] - prev_pos[0]  # الفرق في X
            dy = self.robot.position[1] - prev_pos[1]  # الفرق في Y
            if dx != 0 or dy != 0:  # إذا تحرك
                # رسم سهم يوضح اتجاه حركة الروبوت
                self.ax.arrow(self.robot.position[0], self.robot.position[1], 
                            dx, dy, head_width=1.5, head_length=2, 
                            fc='darkgreen', ec='darkgreen', alpha=0.8)
        
        self.ax.plot(self.env.start[0], self.env.start[1], 'go', markersize=20,  # رسم نقطة البداية
                    label='Start', markeredgecolor='black', markeredgewidth=2)
        self.ax.plot(self.env.goal[0], self.env.goal[1], 'ro', markersize=20,  # رسم نقطة الهدف
                    label='Goal', markeredgecolor='black', markeredgewidth=2)
        
        if not self.robot.reached_goal:  # إذا لم يصل الروبوت للهدف بعد
            self.env.update_dynamic_obstacles()  # تحديث مواقع العقبات المتحركة
            self.robot.move()  # تحريك الروبوت خطوة واحدة
        
        status = "GOAL REACHED! " if self.robot.reached_goal else f"Moving... Frame: {frame}"  # حالة الروبوت
        if self.robot.collision_detected:  # إذا كان هناك تصادم
            status = "COLLISION! Waiting..." + status  # تحديث الحالة
        if self.robot.avoidance_mode:  # إذا كان في وضع التجنب
            status = "AVOIDING Obstacle! " + status  # تحديث الحالة
        if self.robot.stuck_counter > 10:  # إذا كان الروبوت عالقاً
            status = "STUCK! Recovering... " + status  # تحديث الحالة
            
        goal_distance = math.sqrt((self.robot.position[0]-self.env.goal[0])**2 +  # حساب المسافة للهدف
                                (self.robot.position[1]-self.env.goal[1])**2)
        
        self.ax.set_title(f'Enhanced GA Robot Path Planning - {status}\n'  # تعيين العنوان
                         f'Distance Traveled: {self.robot.distance_traveled:.1f} | '
                         f'Distance to Goal: {goal_distance:.1f} | '
                         f'Time Step: {self.env.time_step}',
                         fontsize=14, fontweight='bold')
        
        self.ax.legend(loc='upper right', fontsize=10)  # إضافة وسيلة الإيضاح
        self.ax.set_xlim(0, self.env.width)  # تحديد حدود المحور X
        self.ax.set_ylim(0, self.env.height)  # تحديد حدود المحور Y
        self.ax.grid(True, alpha=0.3)  # إظهار الشبكة
        self.ax.set_aspect('equal')  # جعل المحورين متساويين في القياس
        
        self.ax.set_xlabel('X Position')  # تسمية المحور X
        self.ax.set_ylabel('Y Position')  # تسمية المحور Y
        
        if frame % 20 == 0 and not self.robot.reached_goal:  # كل 20 إطار
            print(f"   Frame {frame}: Position {self.robot.position}, Distance to goal: {goal_distance:.1f}")  # طباعة المعلومات
        
        return []  # إرجاع قائمة فارغة (مطلوب لـ FuncAnimation)
    
    def calculate_required_steps(self):
        """حساب عدد الخطوات المطلوبة للوصول للهدف"""
        if not self.best_path.points:  # إذا لم يكن هناك مسار
            return 200  # أرجع 200 إطار افتراضياً
        
        total_distance = 0  # تهيئة المسافة الكلية
        for i in range(len(self.best_path.points) - 1):  # حساب مسافة المسار الأمثل
            point1 = self.best_path.points[i]  # النقطة الأولى
            point2 = self.best_path.points[i + 1]  # النقطة الثانية
            total_distance += math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)  # إضافة المسافة
        
        last_point = self.best_path.points[-1]  # آخر نقطة في المسار
        goal_point = self.env.goal  # نقطة الهدف
        total_distance += math.sqrt((last_point[0]-goal_point[0])**2 + (last_point[1]-goal_point[1])**2)  # إضافة المسافة للهدف
        
        estimated_steps = int(total_distance / self.robot.speed) + 50  # حساب الخطوات + 50 احتياطي
        return min(max(estimated_steps, 100), 400)  # الحد الأدنى 100 والحد الأقصى 400




class PathPlanningGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced GA Robot Path Planning")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # فتح النافذة بحجم الشاشة
        
        # متغيرات التخزين
        self.env = None
        self.dga = None
        self.robot = None
        self.best_chrom = None
        self.animation = None
        
        # تخزين تفاصيل العقبات
        self.static_obstacles = []
        self.dynamic_obstacles = []
        
        # إعداد واجهة المستخدم
        self.setup_ui()
        
    def setup_ui(self):
        # إنشاء دفتر تبويب (Notebook) لتنظيم المحتوى
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== التبويب 1: التحكم والإعداد =====
        control_tab = ttk.Frame(notebook)
        notebook.add(control_tab, text="Control & Setup")
        
        # تقسيم التبويب إلى جزأين
        left_frame = ttk.Frame(control_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        right_frame = ttk.Frame(control_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === الجزء الأيسر: إعدادات عامة ===
        general_frame = ttk.LabelFrame(left_frame, text="General Settings", padding="15")
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        # عنوان البرنامج
        title_label = ttk.Label(general_frame, 
                                text="Enhanced GA Robot Path Planning\nStatic & Dynamic Environments",
                                font=('Arial', 16, 'bold'),
                                justify=tk.CENTER)
        title_label.pack(pady=(0, 20))
        
        # اختيار نوع البيئة
        env_frame = ttk.LabelFrame(general_frame, text="Environment Type", padding="10")
        env_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.env_type = tk.StringVar(value="static")
        ttk.Radiobutton(env_frame, text="Static Environment (Only static obstacles)", 
                       variable=self.env_type, value="static").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(env_frame, text="Dynamic Environment (Static + dynamic obstacles)", 
                       variable=self.env_type, value="dynamic").pack(anchor=tk.W, pady=2)
        
        # سرعة الروبوت
        speed_frame = ttk.Frame(general_frame)
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(speed_frame, text="Robot Speed:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(speed_frame, text="(0.5 to 5.0 units per step)", font=('Arial', 9)).pack(anchor=tk.W)
        
        self.speed_var = tk.DoubleVar(value=2.0)
        speed_scale = ttk.Scale(speed_frame, from_=0.5, to=5.0, variable=self.speed_var, 
                               orient=tk.HORIZONTAL, length=200)
        speed_scale.pack(pady=5)
        
        speed_display = ttk.Label(speed_frame, text=f"Current: {self.speed_var.get():.1f}")
        speed_display.pack()
        
        def update_speed_display(*args):
            speed_display.config(text=f"Current: {self.speed_var.get():.1f}")
        
        self.speed_var.trace('w', update_speed_display)
        
        # إعدادات الخوارزمية الجينية
        ga_frame = ttk.LabelFrame(general_frame, text="Genetic Algorithm Settings", padding="10")
        ga_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ga_frame, text="Number of Generations:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.generations_var = tk.IntVar(value=100)
        generations_spinbox = ttk.Spinbox(ga_frame, from_=10, to=500, textvariable=self.generations_var, width=10)
        generations_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(ga_frame, text="Population Size:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.population_var = tk.IntVar(value=40)
        ttk.Spinbox(ga_frame, from_=10, to=200, textvariable=self.population_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # أزرار التحكم الرئيسية
        button_frame = ttk.Frame(general_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        self.setup_env_btn = ttk.Button(button_frame, text="Setup Environment", command=self.setup_environment,
                                       style="Accent.TButton")
        self.setup_env_btn.pack(side=tk.LEFT, padx=5)
        
        self.run_ga_btn = ttk.Button(button_frame, text="Run GA Optimization", command=self.run_ga,
                                    state=tk.DISABLED)
        self.run_ga_btn.pack(side=tk.LEFT, padx=5)
        
        self.animate_btn = ttk.Button(button_frame, text="Start Animation", command=self.start_animation,
                                     state=tk.DISABLED)
        self.animate_btn.pack(side=tk.LEFT, padx=5)
        
        # === الجزء الأيمن: إدارة العقبات ===
        obstacles_frame = ttk.LabelFrame(right_frame, text="Obstacle Management", padding="15")
        obstacles_frame.pack(fill=tk.BOTH, expand=True)
        
        # نظرة عامة على العقبات
        overview_frame = ttk.Frame(obstacles_frame)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(overview_frame, text="Obstacles Overview", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        self.obstacles_text = scrolledtext.ScrolledText(overview_frame, height=8, width=40,
                                                       font=('Courier', 9))
        self.obstacles_text.pack(fill=tk.X, pady=5)
        self.obstacles_text.insert(tk.END, "No obstacles defined yet.\n")
        self.obstacles_text.config(state=tk.DISABLED)
        
        # أزرار إدارة العقبات
        manage_frame = ttk.Frame(obstacles_frame)
        manage_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(manage_frame, text="Add Static Obstacle", 
                  command=self.add_static_obstacle).pack(side=tk.LEFT, padx=2)
        ttk.Button(manage_frame, text="Add Dynamic Obstacle", 
                  command=self.add_dynamic_obstacle).pack(side=tk.LEFT, padx=2)
        ttk.Button(manage_frame, text="Clear All Obstacles", 
                  command=self.clear_obstacles).pack(side=tk.LEFT, padx=2)
        
        # إعدادات الهدف
        goal_frame = ttk.LabelFrame(obstacles_frame, text="Goal Settings", padding="10")
        goal_frame.pack(fill=tk.X)
        
        goal_input_frame = ttk.Frame(goal_frame)
        goal_input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(goal_input_frame, text="X:").pack(side=tk.LEFT, padx=(0, 5))
        self.goal_x_var = tk.IntVar(value=95)
        ttk.Spinbox(goal_input_frame, from_=0, to=100, textvariable=self.goal_x_var, width=8).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(goal_input_frame, text="Y:").pack(side=tk.LEFT, padx=(0, 5))
        self.goal_y_var = tk.IntVar(value=95)
        ttk.Spinbox(goal_input_frame, from_=0, to=100, textvariable=self.goal_y_var, width=8).pack(side=tk.LEFT)
        
        # إضافة عقبات عشوائية
        random_frame = ttk.Frame(obstacles_frame)
        random_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(random_frame, text="Quick Random Obstacles:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(random_frame, text="Add 3 Static", 
                  command=lambda: self.add_random_obstacles(3, False)).pack(side=tk.LEFT, padx=2)
        ttk.Button(random_frame, text="Add 2 Dynamic", 
                  command=lambda: self.add_random_obstacles(2, True)).pack(side=tk.LEFT, padx=2)
        
        # ===== التبويب 2: التصور والرسوم البيانية =====
        visualization_tab = ttk.Frame(notebook)
        notebook.add(visualization_tab, text="Visualization")
        
        # إنشاء إطار للرسوم البيانية
        self.figure = plt.figure(figsize=(14, 10), dpi=100)
        
        # تقسيم الشكل إلى 4 مناطق
        gs = self.figure.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. البيئة والمسار
        self.ax_env = self.figure.add_subplot(gs[0:2, 0:2])
        self.ax_env.set_title("Environment with Path", fontsize=14, fontweight='bold')
        self.ax_env.set_xlabel("X Position", fontsize=11)
        self.ax_env.set_ylabel("Y Position", fontsize=11)
        
        # 2. تطور اللياقة
        self.ax_fitness = self.figure.add_subplot(gs[2, 0])
        self.ax_fitness.set_title("Fitness Evolution", fontsize=12)
        self.ax_fitness.set_xlabel("Generation", fontsize=10)
        self.ax_fitness.set_ylabel("Fitness", fontsize=10)
        
        # 3. تطور المسافة
        self.ax_distance = self.figure.add_subplot(gs[2, 1])
        self.ax_distance.set_title("Distance Evolution", fontsize=12)
        self.ax_distance.set_xlabel("Generation", fontsize=10)
        self.ax_distance.set_ylabel("Distance", fontsize=10)
        
        # إضافة Canvas للشكل
        self.canvas = FigureCanvasTkAgg(self.figure, visualization_tab)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== التبويب 3: الإحصائيات والنتائج =====
        stats_tab = ttk.Frame(notebook)
        notebook.add(stats_tab, text="Statistics & Results")
        
        # إطار النتائج
        results_frame = ttk.LabelFrame(stats_tab, text="Simulation Results", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # منطقة النص للإحصائيات
        self.stats_text = scrolledtext.ScrolledText(results_frame, height=25, width=80,
                                                   font=('Courier', 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # أزرار الإحصائيات
        stats_buttons = ttk.Frame(results_frame)
        stats_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(stats_buttons, text="Update Statistics", 
                  command=self.update_statistics_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(stats_buttons, text="Export to File", 
                  command=self.export_statistics).pack(side=tk.LEFT, padx=5)
        
        # تحديث الواجهة بناءً على نوع البيئة
        self.env_type.trace('w', self.update_ui_for_env_type)
        self.update_ui_for_env_type()
        
        # عرض التعليمات الأولية
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """عرض رسالة ترحيبية وتعليمات"""
        welcome_text = """
╔═══════════════════════════════════════════════════════╗
║   Enhanced GA Robot Path Planning System              ║
╚═══════════════════════════════════════════════════════╝

INSTRUCTIONS:

1. SETUP ENVIRONMENT:
   • Choose environment type (Static/Dynamic)
   • Set robot speed using the slider
   • Add obstacles manually or use random generation
   • Set goal position

2. ADD OBSTACLES:
   • Click "Add Static Obstacle" to add fixed obstacles
   • Click "Add Dynamic Obstacle" to add moving obstacles
   • For dynamic obstacles, you can set position and speed

3. RUN OPTIMIZATION:
   • Click "Setup Environment" to create the environment
   • Click "Run GA Optimization" to find optimal path
   • View results in Visualization tab

4. ANIMATION:
   • Click "Start Animation" to see robot movement

5. VIEW RESULTS:
   • Check Statistics tab for detailed results
   • Visualization tab shows graphs and environment

TIPS:
• Keep obstacles away from start (5,5) and goal positions
• Dynamic obstacles move with positive speed only
• More obstacles = more challenging path planning
"""
        self.stats_text.insert(tk.END, welcome_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def update_ui_for_env_type(self, *args):
        """تحديث واجهة المستخدم بناءً على نوع البيئة المختار"""
        pass  # يمكن إضافة منطق إضافي هنا إذا لزم الأمر
    
    def add_static_obstacle(self):
        """إضافة عقبة ثابتة يدوياً"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Static Obstacle")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # مركز النافذة
        dialog_frame = ttk.Frame(dialog, padding="20")
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(dialog_frame, text="Static Obstacle Settings", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # إدخال الموضع
        position_frame = ttk.LabelFrame(dialog_frame, text="Position (0-100)", padding="10")
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(position_frame, text="X Coordinate:").grid(row=0, column=0, sticky=tk.W, pady=5)
        x_var = tk.IntVar(value=random.randint(20, 80))
        ttk.Spinbox(position_frame, from_=0, to=100, textvariable=x_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(position_frame, text="Y Coordinate:").grid(row=1, column=0, sticky=tk.W, pady=5)
        y_var = tk.IntVar(value=random.randint(20, 80))
        ttk.Spinbox(position_frame, from_=0, to=100, textvariable=y_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # إدخال الحجم
        size_frame = ttk.LabelFrame(dialog_frame, text="Size", padding="10")
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Obstacle Size (5-20):").pack(anchor=tk.W, pady=2)
        size_var = tk.IntVar(value=8)
        ttk.Scale(size_frame, from_=5, to=20, variable=size_var, 
                 orient=tk.HORIZONTAL, length=200).pack(pady=5)
        
        size_display = ttk.Label(size_frame, text=f"Size: {size_var.get()}")
        size_display.pack()
        
        def update_size_display(*args):
            size_display.config(text=f"Size: {size_var.get()}")
        
        size_var.trace('w', update_size_display)
        
        # أزرار
        button_frame = ttk.Frame(dialog_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def add_and_close():
            obstacle = {
                'type': 'static',
                'x': x_var.get(),
                'y': y_var.get(),
                'size': size_var.get()
            }
            self.static_obstacles.append(obstacle)
            self.update_obstacles_display()
            dialog.destroy()
        
        ttk.Button(button_frame, text="Add Obstacle", command=add_and_close,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_dynamic_obstacle(self):
        """إضافة عقبة متحركة يدوياً"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Dynamic Obstacle")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog_frame = ttk.Frame(dialog, padding="20")
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(dialog_frame, text="Dynamic Obstacle Settings", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # إدخال الموضع
        position_frame = ttk.LabelFrame(dialog_frame, text="Position (0-100)", padding="10")
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(position_frame, text="X Coordinate:").grid(row=0, column=0, sticky=tk.W, pady=5)
        x_var = tk.IntVar(value=random.randint(20, 80))
        ttk.Spinbox(position_frame, from_=0, to=100, textvariable=x_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(position_frame, text="Y Coordinate:").grid(row=1, column=0, sticky=tk.W, pady=5)
        y_var = tk.IntVar(value=random.randint(20, 80))
        ttk.Spinbox(position_frame, from_=0, to=100, textvariable=y_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # إدخال الحجم
        size_frame = ttk.LabelFrame(dialog_frame, text="Size", padding="10")
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Obstacle Size (5-20):").pack(anchor=tk.W, pady=2)
        size_var = tk.IntVar(value=8)
        ttk.Scale(size_frame, from_=5, to=20, variable=size_var, 
                 orient=tk.HORIZONTAL, length=200).pack(pady=5)
        
        size_display = ttk.Label(size_frame, text=f"Size: {size_var.get()}")
        size_display.pack()
        
        def update_size_display(*args):
            size_display.config(text=f"Size: {size_var.get()}")
        
        size_var.trace('w', update_size_display)
        
        # إدخال السرعة
        speed_frame = ttk.LabelFrame(dialog_frame, text="Speed (0.1 to 2.0)", padding="10")
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(speed_frame, text="X Speed:").grid(row=0, column=0, sticky=tk.W, pady=5)
        speed_x_var = tk.DoubleVar(value=0.3)
        ttk.Scale(speed_frame, from_=0.1, to=2.0, variable=speed_x_var, 
                 orient=tk.HORIZONTAL, length=150).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        speed_x_display = ttk.Label(speed_frame, text=f"X: {speed_x_var.get():.2f}")
        speed_x_display.grid(row=0, column=2, padx=(10, 0))
        
        ttk.Label(speed_frame, text="Y Speed:").grid(row=1, column=0, sticky=tk.W, pady=5)
        speed_y_var = tk.DoubleVar(value=0.2)
        ttk.Scale(speed_frame, from_=0.1, to=2.0, variable=speed_y_var, 
                 orient=tk.HORIZONTAL, length=150).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        speed_y_display = ttk.Label(speed_frame, text=f"Y: {speed_y_var.get():.2f}")
        speed_y_display.grid(row=1, column=2, padx=(10, 0))
        
        def update_speed_displays(*args):
            speed_x_display.config(text=f"X: {speed_x_var.get():.2f}")
            speed_y_display.config(text=f"Y: {speed_y_var.get():.2f}")
        
        speed_x_var.trace('w', update_speed_displays)
        speed_y_var.trace('w', update_speed_displays)
        
        # أزرار
        button_frame = ttk.Frame(dialog_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def add_and_close():
            obstacle = {
                'type': 'dynamic',
                'x': x_var.get(),
                'y': y_var.get(),
                'size': size_var.get(),
                'speed_x': speed_x_var.get(),
                'speed_y': speed_y_var.get()
            }
            self.dynamic_obstacles.append(obstacle)
            self.update_obstacles_display()
            dialog.destroy()
        
        ttk.Button(button_frame, text="Add Obstacle", command=add_and_close,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_random_obstacles(self, count, is_dynamic):
        """إضافة عقبات عشوائية"""
        for _ in range(count):
            if is_dynamic:
                obstacle = {
                    'type': 'dynamic',
                    'x': random.randint(20, 80),
                    'y': random.randint(20, 80),
                    'size': random.randint(5, 15),
                    'speed_x': random.uniform(0.1, 0.8),
                    'speed_y': random.uniform(0.1, 0.8)
                }
                self.dynamic_obstacles.append(obstacle)
            else:
                obstacle = {
                    'type': 'static',
                    'x': random.randint(20, 80),
                    'y': random.randint(20, 80),
                    'size': random.randint(5, 15)
                }
                self.static_obstacles.append(obstacle)
        
        self.update_obstacles_display()
        messagebox.showinfo("Success", f"Added {count} random {'dynamic' if is_dynamic else 'static'} obstacles")
    
    def clear_obstacles(self):
        """حذف جميع العقبات"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all obstacles?"):
            self.static_obstacles.clear()
            self.dynamic_obstacles.clear()
            self.update_obstacles_display()
    
    def update_obstacles_display(self):
        """تحديث عرض العقبات"""
        self.obstacles_text.config(state=tk.NORMAL)
        self.obstacles_text.delete(1.0, tk.END)
        
        if not self.static_obstacles and not self.dynamic_obstacles:
            self.obstacles_text.insert(tk.END, "No obstacles defined yet.\n")
        else:
            # عرض العقبات الثابتة
            if self.static_obstacles:
                self.obstacles_text.insert(tk.END, "STATIC OBSTACLES:\n")
                self.obstacles_text.insert(tk.END, "─" * 40 + "\n")
                for i, obs in enumerate(self.static_obstacles, 1):
                    self.obstacles_text.insert(tk.END, 
                        f"{i:2d}. Position: ({obs['x']:3d}, {obs['y']:3d}) | Size: {obs['size']:2d}\n")
                self.obstacles_text.insert(tk.END, "\n")
            
            # عرض العقبات المتحركة
            if self.dynamic_obstacles:
                self.obstacles_text.insert(tk.END, "DYNAMIC OBSTACLES:\n")
                self.obstacles_text.insert(tk.END, "─" * 40 + "\n")
                for i, obs in enumerate(self.dynamic_obstacles, 1):
                    total_speed = math.sqrt(obs['speed_x']**2 + obs['speed_y']**2)
                    self.obstacles_text.insert(tk.END, 
                        f"{i:2d}. Position: ({obs['x']:3d}, {obs['y']:3d}) | "
                        f"Size: {obs['size']:2d} | "
                        f"Speed: ({obs['speed_x']:.2f}, {obs['speed_y']:.2f}) | "
                        f"Total: {total_speed:.2f}\n")
        
        self.obstacles_text.config(state=tk.DISABLED)
    
    def setup_environment(self):
        """إعداد البيئة بناءً على إعدادات المستخدم"""
        try:
            # التحقق من المدخلات
            speed = self.speed_var.get()
            if speed < 0.5 or speed > 5.0:
                messagebox.showerror("Invalid Input", "Robot speed must be between 0.5 and 5.0")
                return
            
            # إنشاء بيئة جديدة
            self.env = Environment(100, 100)
            self.env.set_start_goal(5, 5, self.goal_x_var.get(), self.goal_y_var.get())
            
            # إضافة العقبات الثابتة
            for obs in self.static_obstacles:
                vertices = [
                    (obs['x'], obs['y']),
                    (obs['x'] + obs['size'], obs['y']),
                    (obs['x'] + obs['size'], obs['y'] + obs['size']),
                    (obs['x'], obs['y'] + obs['size'])
                ]
                self.env.add_obstacle(Obstacle(vertices, is_dynamic=False))
            
            # إضافة العقبات المتحركة
            for obs in self.dynamic_obstacles:
                vertices = [
                    (obs['x'], obs['y']),
                    (obs['x'] + obs['size'], obs['y']),
                    (obs['x'] + obs['size'], obs['y'] + obs['size']),
                    (obs['x'], obs['y'] + obs['size'])
                ]
                self.env.add_obstacle(Obstacle(
                    vertices,
                    is_dynamic=True,
                    velocity=(obs['speed_x'], obs['speed_y'])
                ))
            
            # عرض البيئة
            self.visualize_environment("Initial Environment Setup")
            
            # تمكين الأزرار
            self.run_ga_btn.config(state=tk.NORMAL)
            self.animate_btn.config(state=tk.DISABLED)
            self.update_statistics_display()
            
            messagebox.showinfo("Success", 
                              f"Environment setup completed!\n\n"
                              f"• Static obstacles: {len(self.static_obstacles)}\n"
                              f"• Dynamic obstacles: {len(self.dynamic_obstacles)}\n"
                              f"• Robot speed: {speed:.1f}\n"
                              f"• Goal: ({self.goal_x_var.get()}, {self.goal_y_var.get()})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up environment:\n{str(e)}")
    
    def visualize_environment(self, title):
        """عرض البيئة الحالية"""
        self.ax_env.clear()
        
        # رسم العقبات
        for obstacle in self.env.obstacles:
            vertices = obstacle.vertices
            x_coords = [v[0] for v in vertices] + [vertices[0][0]]
            y_coords = [v[1] for v in vertices] + [vertices[0][1]]
            
            color = '#FFA500' if obstacle.is_dynamic else '#FF4444'  # برتقالي لأحمر
            alpha = 0.6 if obstacle.is_dynamic else 0.7
            
            label = "Dynamic Obstacles" if obstacle.is_dynamic else "Static Obstacles"
            self.ax_env.fill(x_coords, y_coords, color, alpha=alpha, label=label, edgecolor='black', linewidth=1)
            
            # إضافة نص للمساعدة في الرؤية
            center_x = sum(v[0] for v in vertices) / len(vertices)
            center_y = sum(v[1] for v in vertices) / len(vertices)
            
            if obstacle.is_dynamic:
                # إضافة سهم يوضح اتجاه الحركة
                dx, dy = obstacle.velocity
                if dx != 0 or dy != 0:
                    self.ax_env.arrow(center_x, center_y, dx*2, dy*2, 
                                    head_width=1.5, head_length=2, 
                                    fc='yellow', ec='yellow', alpha=0.8)
                self.ax_env.text(center_x, center_y, 'D', 
                               fontsize=8, fontweight='bold',
                               ha='center', va='center',
                               color='white', bbox=dict(boxstyle="circle,pad=0.3", facecolor=color))
            else:
                self.ax_env.text(center_x, center_y, 'S', 
                               fontsize=8, fontweight='bold',
                               ha='center', va='center',
                               color='white', bbox=dict(boxstyle="circle,pad=0.3", facecolor=color))
        
        # رسم نقطتي البداية والهدف
        if self.env.start:
            self.ax_env.plot(self.env.start[0], self.env.start[1], 'go', 
                           markersize=20, markeredgewidth=2, markeredgecolor='black',
                           label='Start')
            self.ax_env.text(self.env.start[0], self.env.start[1] + 3, 'START',
                           fontsize=10, fontweight='bold', ha='center', color='green')
        
        if self.env.goal:
            self.ax_env.plot(self.env.goal[0], self.env.goal[1], 'ro', 
                           markersize=20, markeredgewidth=2, markeredgecolor='black',
                           label='Goal')
            self.ax_env.text(self.env.goal[0], self.env.goal[1] + 3, 'GOAL',
                           fontsize=10, fontweight='bold', ha='center', color='red')
        
        self.ax_env.set_xlim(0, self.env.width)
        self.ax_env.set_ylim(0, self.env.height)
        self.ax_env.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax_env.legend(loc='upper right', fontsize=10)
        self.ax_env.set_title(title, fontsize=16, fontweight='bold', pad=20)
        self.ax_env.set_xlabel('X Position', fontsize=12)
        self.ax_env.set_ylabel('Y Position', fontsize=12)
        self.ax_env.set_aspect('equal')
        
        # إضافة إحداثيات للمساعدة في الرؤية
        self.ax_env.text(0.02, 0.98, f'Start: {self.env.start}', 
                        transform=self.ax_env.transAxes,
                        fontsize=9, verticalalignment='top',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        self.ax_env.text(0.02, 0.93, f'Goal: {self.env.goal}', 
                        transform=self.ax_env.transAxes,
                        fontsize=9, verticalalignment='top',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # مسح الرسوم البيانية الأخرى
        self.clear_plots()
        
        self.canvas.draw()
    
    def clear_plots(self):
        """مسح الرسوم البيانية"""
        self.ax_fitness.clear()
        self.ax_fitness.set_title("Fitness Evolution", fontsize=12)
        self.ax_fitness.set_xlabel("Generation", fontsize=10)
        self.ax_fitness.set_ylabel("Fitness", fontsize=10)
        self.ax_fitness.grid(True, alpha=0.3)
        
        
       

    
    def run_ga(self):
        """تشغيل الخوارزمية الجينية"""
        try:
            if not self.env:
                messagebox.showerror("Error", "Please setup environment first!")
                return
            
            # إنشاء خوارزمية جينية
            self.dga = DynamicGeneticAlgorithm(
                env=self.env,
                population_size=self.population_var.get(),
                crossover_prob=0.75,
                mutation_prob=0.3,
                elitism_count=2,
                tournament_size=3,
                memory_size=10,
                random_immigrants_ratio=0.2
            )
            
            # إعداد أحداث ديناميكية
            dynamic_events = []
            if self.env_type.get() == "dynamic" and self.dynamic_obstacles:
                sample_obs = self.dynamic_obstacles[0] if self.dynamic_obstacles else {'size': 8}
                dynamic_events = [
                    {'generation': 25, 'type': 'add_obstacle', 'size': sample_obs['size'], 'dynamic': False},
                    {'generation': 50, 'type': 'add_obstacle', 'size': sample_obs['size'], 'dynamic': True},
                    {'generation': 75, 'type': 'change_goal', 'new_goal': (90, 60)}
                ]
            
            # نافذة التقدم
            progress_window = tk.Toplevel(self.root)
            progress_window.title("GA Optimization Progress")
            progress_window.geometry("500x200")
            progress_window.transient(self.root)
            
            progress_frame = ttk.Frame(progress_window, padding="20")
            progress_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(progress_frame, text="Running Genetic Algorithm...", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 20))
            
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, 
                                         maximum=self.generations_var.get(), length=400)
            progress_bar.pack(pady=10)
            
            status_label = ttk.Label(progress_frame, text="Initializing...", font=('Arial', 10))
            status_label.pack(pady=5)
            
            details_label = ttk.Label(progress_frame, text="", font=('Arial', 9))
            details_label.pack(pady=5)
            
            progress_window.update()
            
            # تهيئة المجتمع
            self.dga.initialize_population()
            
            # تشغيل الأجيال
            generations = self.generations_var.get()
            for gen in range(generations):
                self.dga.run_generation()
                
                # تحديث التقدم
                progress_var.set(gen + 1)
                status_label.config(text=f"Generation: {gen+1}/{generations}")
                
                # تحديث التفاصيل كل 10 أجيال
                if gen % 10 == 0 or gen == generations - 1:
                    stats = self.dga.get_statistics()
                    details = (f"Best Fitness: {stats.get('best_fitness', 0):.6f} | "
                             f"Best Distance: {stats.get('best_distance', 0):.2f} | "
                             f"Feasible: {stats.get('feasible_ratio', 0):.1%}")
                    details_label.config(text=details)
                
                # تحديث الرسوم البيانية كل 5 أجيال
                if gen % 5 == 0 or gen == generations - 1:
                    self.update_plots()
                
                progress_window.update()
            
            progress_window.destroy()
            
            # الحصول على أفضل مسار
            self.best_chrom = self.dga.get_best_chromosome()
            
            # عرض المسار الأمثل
            self.visualize_with_path()
            
            # تمكين زر الرسوم المتحركة
            self.animate_btn.config(state=tk.NORMAL)
            
            # تحديث الإحصائيات
            self.update_statistics_display()
            
            messagebox.showinfo("GA Completed", 
                              f"✅ Genetic Algorithm completed successfully!\n\n"
                              f"📊 Results:\n"
                              f"• Best path distance: {self.best_chrom.total_distance:.2f}\n"
                              f"• Path feasible: {self.best_chrom.is_feasible}\n"
                              f"• Generations: {generations}\n"
                              f"• Environment changes handled: {self.dga.environment_changes}\n\n"
                              f"Click 'Start Animation' to see the robot movement!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error running GA:\n{str(e)}")
    
    def update_plots(self):
        """تحديث جميع الرسوم البيانية"""
        if not self.dga:
            return
        
        # تحديث رسم اللياقة
        self.ax_fitness.clear()
        if self.dga.best_fitness_history:
            generations = list(range(1, len(self.dga.best_fitness_history) + 1))
            self.ax_fitness.plot(generations, self.dga.best_fitness_history, 
                               'b-', linewidth=2, label='Best Fitness')
            
            if self.dga.average_fitness_history:
                self.ax_fitness.plot(generations, self.dga.average_fitness_history,
                                   'g--', linewidth=1.5, alpha=0.7, label='Average Fitness')
            
            self.ax_fitness.set_title("Fitness Evolution", fontsize=12, fontweight='bold')
            self.ax_fitness.set_xlabel("Generation", fontsize=10)
            self.ax_fitness.set_ylabel("Fitness (Higher is better)", fontsize=10)
            self.ax_fitness.legend(fontsize=9)
            self.ax_fitness.grid(True, alpha=0.3)
        
        # تحديث رسم المسافة (سيتم إضافته لاحقاً)
        self.ax_distance.clear()
        self.ax_distance.set_title("Distance Evolution", fontsize=12, fontweight='bold')
        self.ax_distance.set_xlabel("Generation", fontsize=10)
        self.ax_distance.set_ylabel("Distance", fontsize=10)
        self.ax_distance.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def visualize_with_path(self):
        """عرض البيئة مع المسار الأمثل"""
        self.ax_env.clear()
        
        # رسم العقبات
        for obstacle in self.env.obstacles:
            vertices = obstacle.vertices
            x_coords = [v[0] for v in vertices] + [vertices[0][0]]
            y_coords = [v[1] for v in vertices] + [vertices[0][1]]
            
            color = '#FFA500' if obstacle.is_dynamic else '#FF4444'
            alpha = 0.6 if obstacle.is_dynamic else 0.7
            
            label = "Dynamic Obstacles" if obstacle.is_dynamic else "Static Obstacles"
            self.ax_env.fill(x_coords, y_coords, color, alpha=alpha, label=label, edgecolor='black', linewidth=1)
        
        # رسم المسار الأمثل
        if self.best_chrom and self.best_chrom.points:
            x_coords = [p[0] for p in self.best_chrom.points]
            y_coords = [p[1] for p in self.best_chrom.points]
            
            # اختيار اللون بناءً على إمكانية المسار
            if self.best_chrom.is_feasible:
                path_color = '#0066CC'  # أزرق
                path_style = '-'
                path_label = f'Optimal Path (Distance: {self.best_chrom.total_distance:.2f})'
            else:
                path_color = '#CC0000'  # أحمر
                path_style = '--'
                path_label = f'Infeasible Path (Distance: {self.best_chrom.total_distance:.2f})'
            
            self.ax_env.plot(x_coords, y_coords, path_style, color=path_color, 
                           linewidth=3, alpha=0.8, label=path_label, marker='o', 
                           markersize=6, markerfacecolor='white', markeredgecolor=path_color)
            
            # إضافة أرقام للنقاط
            for i, (x, y) in enumerate(self.best_chrom.points):
                if i > 0 and i < len(self.best_chrom.points) - 1:  # تجنب البداية والنهاية
                    self.ax_env.text(x, y + 1.5, str(i), fontsize=8, fontweight='bold',
                                   ha='center', va='center',
                                   bbox=dict(boxstyle="circle,pad=0.2", facecolor='white', alpha=0.8))
        
        # رسم نقطتي البداية والهدف
        if self.env.start:
            self.ax_env.plot(self.env.start[0], self.env.start[1], 'go', 
                           markersize=25, markeredgewidth=3, markeredgecolor='black',
                           label='Start', zorder=10)
            self.ax_env.text(self.env.start[0], self.env.start[1] + 4, 'START',
                           fontsize=11, fontweight='bold', ha='center', color='green')
        
        if self.env.goal:
            self.ax_env.plot(self.env.goal[0], self.env.goal[1], 'ro', 
                           markersize=25, markeredgewidth=3, markeredgecolor='black',
                           label='Goal', zorder=10)
            self.ax_env.text(self.env.goal[0], self.env.goal[1] + 4, 'GOAL',
                           fontsize=11, fontweight='bold', ha='center', color='red')
        
        self.ax_env.set_xlim(0, self.env.width)
        self.ax_env.set_ylim(0, self.env.height)
        self.ax_env.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # تحسين وسيلة الإيضاح
        handles, labels = self.ax_env.get_legend_handles_labels()
        if handles:
            self.ax_env.legend(handles, labels, loc='upper right', fontsize=10, 
                             framealpha=0.9, shadow=True)
        
        self.ax_env.set_title("Environment with GA Optimized Path", fontsize=16, fontweight='bold', pad=20)
        self.ax_env.set_xlabel('X Position', fontsize=12)
        self.ax_env.set_ylabel('Y Position', fontsize=12)
        self.ax_env.set_aspect('equal')
        
        # إضافة معلومات إضافية
        if self.best_chrom:
            info_text = (f"Path Distance: {self.best_chrom.total_distance:.2f}\n"
                        f"Feasible: {'Yes' if self.best_chrom.is_feasible else 'No'}\n"
                        f"Waypoints: {len(self.best_chrom.points)}")
            
            self.ax_env.text(0.98, 0.02, info_text, 
                           transform=self.ax_env.transAxes,
                           fontsize=10, fontweight='bold',
                           verticalalignment='bottom', horizontalalignment='right',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9))
        
        self.canvas.draw()
    
    def start_animation(self):
        """بدء الرسوم المتحركة للروبوت"""
        if not self.env or not self.best_chrom:
            messagebox.showerror("Error", "Please run GA optimization first!")
            return
        
        try:
            # إنشاء الروبوت
            speed = self.speed_var.get()
            self.robot = Robot(self.env.start, self.env)
            self.robot.speed = speed
            
            # إنشاء الرسوم المتحركة
            self.animation = MatplotlibAnimation(self.env, self.robot, self.best_chrom)
            
            # تشغيل الرسوم المتحركة في نافذة منفصلة
            # (سيتم فتح نافذة matplotlib منفصلة)
            messagebox.showinfo("Animation", 
                              "The animation will open in a separate window.\n\n"
                              "Close the animation window when finished.")
            
            # تشغيل المحاكاة
            self.animation.simulate_movement()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error starting animation:\n{str(e)}")
    
    def update_statistics_display(self):
        """تحديث عرض الإحصائيات"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        # معلومات البيئة
        self.stats_text.insert(tk.END, "═" * 70 + "\n")
        self.stats_text.insert(tk.END, "ENVIRONMENT INFORMATION\n")
        self.stats_text.insert(tk.END, "═" * 70 + "\n\n")
        
        if self.env:
            self.stats_text.insert(tk.END, f"Environment Type: {self.env_type.get().upper()}\n")
            self.stats_text.insert(tk.END, f"Robot Speed: {self.speed_var.get():.2f}\n")
            self.stats_text.insert(tk.END, f"Start Position: {self.env.start}\n")
            self.stats_text.insert(tk.END, f"Goal Position: {self.env.goal}\n")
            self.stats_text.insert(tk.END, f"Static Obstacles: {len(self.static_obstacles)}\n")
            self.stats_text.insert(tk.END, f"Dynamic Obstacles: {len(self.dynamic_obstacles)}\n")
        else:
            self.stats_text.insert(tk.END, "Environment not yet configured.\n")
        
        self.stats_text.insert(tk.END, "\n" + "─" * 70 + "\n\n")
        
        # معلومات العقبات
        self.stats_text.insert(tk.END, "OBSTACLES DETAILS\n")
        self.stats_text.insert(tk.END, "─" * 70 + "\n\n")
        
        if self.static_obstacles:
            self.stats_text.insert(tk.END, "Static Obstacles:\n")
            for i, obs in enumerate(self.static_obstacles, 1):
                self.stats_text.insert(tk.END, 
                    f"  {i:2d}. Position: ({obs['x']:3d}, {obs['y']:3d}) | Size: {obs['size']:2d}\n")
            self.stats_text.insert(tk.END, "\n")
        
        if self.dynamic_obstacles:
            self.stats_text.insert(tk.END, "Dynamic Obstacles:\n")
            for i, obs in enumerate(self.dynamic_obstacles, 1):
                total_speed = math.sqrt(obs['speed_x']**2 + obs['speed_y']**2)
                self.stats_text.insert(tk.END, 
                    f"  {i:2d}. Position: ({obs['x']:3d}, {obs['y']:3d}) | "
                    f"Size: {obs['size']:2d} | "
                    f"Velocity: ({obs['speed_x']:.2f}, {obs['speed_y']:.2f}) | "
                    f"Total Speed: {total_speed:.2f}\n")
        
        if not self.static_obstacles and not self.dynamic_obstacles:
            self.stats_text.insert(tk.END, "No obstacles defined.\n")
        
        self.stats_text.insert(tk.END, "\n" + "─" * 70 + "\n\n")
        
        # معلومات GA إذا كانت متاحة
        if self.dga:
            stats = self.dga.get_statistics()
            
            self.stats_text.insert(tk.END, "GENETIC ALGORITHM RESULTS\n")
            self.stats_text.insert(tk.END, "─" * 70 + "\n\n")
            
            self.stats_text.insert(tk.END, f"Generations: {stats.get('generation', 0)}\n")
            self.stats_text.insert(tk.END, f"Population Size: {self.population_var.get()}\n")
            self.stats_text.insert(tk.END, f"Environment Changes: {stats.get('environment_changes', 0)}\n")
            self.stats_text.insert(tk.END, f"Memory Size: {stats.get('memory_size', 0)}\n\n")
            
            self.stats_text.insert(tk.END, "Fitness Statistics:\n")
            self.stats_text.insert(tk.END, f"  Best Fitness: {stats.get('best_fitness', 0):.6f}\n")
            self.stats_text.insert(tk.END, f"  Worst Fitness: {stats.get('worst_fitness', 0):.6f}\n")
            self.stats_text.insert(tk.END, f"  Average Fitness: {stats.get('average_fitness', 0):.6f}\n")
            self.stats_text.insert(tk.END, f"  Feasible Paths Ratio: {stats.get('feasible_ratio', 0):.2%}\n\n")
            
            self.stats_text.insert(tk.END, "Distance Statistics:\n")
            self.stats_text.insert(tk.END, f"  Best Distance: {stats.get('best_distance', 0):.2f}\n")
            self.stats_text.insert(tk.END, f"  Worst Distance: {stats.get('worst_distance', 0):.2f}\n")
            self.stats_text.insert(tk.END, f"  Average Distance: {stats.get('average_distance', 0):.2f}\n\n")
            
            if self.best_chrom:
                self.stats_text.insert(tk.END, "BEST PATH INFORMATION:\n")
                self.stats_text.insert(tk.END, f"  Total Distance: {self.best_chrom.total_distance:.2f}\n")
                self.stats_text.insert(tk.END, f"  Feasible: {self.best_chrom.is_feasible}\n")
                self.stats_text.insert(tk.END, f"  Number of Waypoints: {len(self.best_chrom.points)}\n")
                self.stats_text.insert(tk.END, f"  Collision Length: {self.best_chrom.collision_length:.2f}\n")
        
        self.stats_text.insert(tk.END, "\n" + "═" * 70 + "\n")
        self.stats_text.config(state=tk.DISABLED)
    
    def export_statistics(self):
        """تصدير الإحصائيات إلى ملف"""
        try:
            from datetime import datetime
            import json
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"path_planning_stats_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.stats_text.get(1.0, tk.END))
            
            messagebox.showinfo("Export Successful", 
                              f"Statistics exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting statistics:\n{str(e)}")

def test_enhanced_ga():
    """تشغيل الواجهة الرسومية"""
    root = tk.Tk()
    
    # إضافة بعض الأنماط
    style = ttk.Style()
    style.theme_use('clam')
    
    # تخصيص الأنماط
    style.configure('Accent.TButton', font=('Arial', 11, 'bold'), padding=10)
    style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
    
    app = PathPlanningGUI(root)
    root.mainloop()

if __name__ == "__main__":
    test_enhanced_ga()