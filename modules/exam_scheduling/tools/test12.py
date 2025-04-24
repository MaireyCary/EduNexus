import logging
import random
from collections import defaultdict
import json
from .parameter import place, classes, week


class ExamScheduler:
    def __init__(self, class_course_dict):
        # 核心算法参数（可在实例化时通过参数修改）
        self.population_size = 100  # 种群规模
        self.generations = 100  # 迭代代数
        self.mutation_rate = 0.05  # 变异概率
        self.selection_ratio = 0.8  # 选择比例

        # 直接使用传入的班级课程对应关系
        self.class_course_dict = class_course_dict

        # 数据预处理
        self._preprocess_data()

        # 系统约束参数
        self.place = place
        self.time_slots = [(i, j) for i in range(len(week))
                           for j in range(len(classes))]  # 时间槽

    def _preprocess_data(self):
        """数据预处理（封装为类方法）"""
        self.all_teachers = set()
        self.exams = []

        for class_name, class_info in self.class_course_dict.items():
            for course in class_info:
                course_name, teacher_names = course
                teachers = [teacher_names.strip()]
                self.exams.append({
                    'class': class_name,
                    'course': course_name,
                    'teachers': teachers
                })
                self.all_teachers.update(teachers)

        self.all_teachers = list(self.all_teachers)

    def create_individual(self):
        """创建个体（保持原有逻辑，仅调整变量引用）"""
        individual = []
        teacher_availability = {teacher: self.time_slots.copy() for teacher in self.all_teachers}

        for exam in self.exams:
            main_teachers = exam['teachers']
            if len(main_teachers) >= 2:
                selected = random.sample(main_teachers, 2)
            else:
                available = [t for t in self.all_teachers if t not in main_teachers]
                selected = main_teachers + random.sample(available, 1)

            valid_time_slots = set(self.time_slots)
            for teacher in selected:
                valid_time_slots = valid_time_slots.intersection(set(teacher_availability[teacher]))

            if valid_time_slots:
                time_slot = random.choice(list(valid_time_slots))
                for teacher in selected:
                    teacher_availability[teacher].remove(time_slot)
            else:
                # 如果没有可用时间槽，随机选择一个
                time_slot = random.choice(self.time_slots)

            classroom = random.choice(self.place)
            individual.append({
                'class': exam['class'],
                'course': exam['course'],
                'teachers': selected,
                'time': time_slot,
                'classroom': classroom
            })
        return individual

    def calculate_fitness(self, individual):
        """计算适应度（保持原有逻辑）"""
        conflict_count = 0
        room_usage = defaultdict(set)
        teacher_schedule = defaultdict(set)

        for exam in individual:
            time_key = exam['time']
            room_key = (time_key, exam['classroom'])

            if exam['classroom'] in room_usage[time_key]:
                conflict_count += 1
            room_usage[time_key].add(exam['classroom'])

            for teacher in exam['teachers']:
                teacher_key = (time_key, teacher)
                if teacher_key in teacher_schedule:
                    conflict_count += 1
                teacher_schedule[teacher_key].add(exam['classroom'])

        return 1 / (conflict_count + 1)

    def crossover(self, parent1, parent2):
        """交叉操作（保持原有逻辑）"""
        split_point = random.randint(1, len(parent1) - 1)
        return parent1[:split_point] + parent2[split_point:], parent2[:split_point] + parent1[split_point:]

    def mutate(self, individual):
        """变异操作（使用类属性的mutation_rate）"""
        teacher_availability = {teacher: self.time_slots.copy() for teacher in self.all_teachers}
        for exam in individual:
            for teacher in exam['teachers']:
                if exam['time'] in teacher_availability[teacher]:
                    teacher_availability[teacher].remove(exam['time'])

        for exam in individual:
            if random.random() < self.mutation_rate:
                valid_time_slots = set(self.time_slots)
                for teacher in exam['teachers']:
                    valid_time_slots = valid_time_slots.intersection(set(teacher_availability[teacher]))

                if valid_time_slots:
                    new_time_slot = random.choice(list(valid_time_slots))
                    for teacher in exam['teachers']:
                        teacher_availability[teacher].remove(new_time_slot)
                    exam['time'] = new_time_slot
                else:
                    exam['time'] = random.choice(self.time_slots)

            if random.random() < self.mutation_rate:
                exam['classroom'] = random.choice(self.place)
            if (random.random() < self.mutation_rate and
                    len(exam['teachers']) >= 2):
                exam['teachers'] = random.sample(self.all_teachers, 2)
        return individual

    def select_parents(self, scored_population):
        """选择父代（基于选择比例）"""
        total_fitness = sum(score for score, _ in scored_population)
        probabilities = [score / total_fitness for score, _ in scored_population]
        return random.choices(scored_population, weights=probabilities,
                              k=int(self.population_size * self.selection_ratio))

    def run(self):
        """运行遗传算法（封装主流程）"""
        population = [self.create_individual() for _ in range(self.population_size)]
        best_schedule = None
        best_score = 0

        for generation in range(self.generations):
            scored = [(self.calculate_fitness(ind), ind) for ind in population]

            if not scored:
                raise ValueError("No valid solutions")

            scored.sort(reverse=True, key=lambda x: x[0])
            current_best = scored[0]

            if current_best[0] > best_score:
                best_score, best_schedule = current_best

            # 精英保留策略
            population = [ind for score, ind in scored[:20]]

            # 选择、交叉、变异
            selected = self.select_parents(scored)
            next_generation = []

            for i in range(0, len(selected), 2):
                parent1, parent2 = selected[i][1], selected[i + 1][1]
                child1, child2 = self.crossover(parent1, parent2)
                next_generation.extend([self.mutate(child1), self.mutate(child2)])

            population = next_generation[:self.population_size]


        return best_schedule

    def generate_json_schedule(self, schedule, output_path):
        """
        将考试安排结果转换为指定格式的JSON文件
        :param schedule: 考试安排结果
        :param output_path: JSON文件的存储路径
        """
        class_schedule = {}
        for idx, exam in enumerate(schedule):
            class_name = exam['class']
            time_str = f"{week[exam['time'][0]]} {classes[exam['time'][1]]}"
            exam_info = {
                'examId': f"考试{idx + 1}",
                'examName': exam['course'],
                'time': time_str,
                'classroom': exam['classroom'],
                'teachers': exam['teachers']
            }
            if class_name not in class_schedule:
                class_schedule[class_name] = []
            class_schedule[class_name].append(exam_info)

        json_data = {
            "classes": [
                {
                    "classId": class_name,
                    "exams": exams
                }
                for class_name, exams in class_schedule.items()
            ]
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"保存JSON文件时出错: {e}")
