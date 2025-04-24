import random
from . import parameter

# 定义遗传算法的参数
population_size = 100  # 种群大小
generations = 50  # 迭代次数
mutation_rate = 0.05  # 变异概率


def initialize_population(population_size, class_data):
    """
    初始化种群，随机生成每个课程的排课方案
    """
    population = []
    for _ in range(population_size):
        schedule = {}
        for teacher, courses in class_data.items():
            for course in courses:
                day = random.choice(parameter.week)
                period = random.choice(parameter.classes)
                place = random.choice(parameter.place)
                schedule[(teacher, course)] = {"星期": day, "时间段": period, "教室": place}
        population.append(schedule)
    return population


def fitness(schedule, class_data, public_positions):
    """
    计算排课方案的适应度
    """
    fitness_score = 0

    for (teacher, course), info in schedule.items():
        course_info = class_data[teacher][course]
        place_requirements = course_info["场地要求"]

        # 检查场地要求是否有明确要求
        if isinstance(place_requirements, str):
            required_places = place_requirements.split("或")
            if info["教室"] in required_places:
                fitness_score += 1  # 场地要求被满足时加分
        # 如果没有场地要求或为其他则不加分
        else:
            pass

        # 检查是否冲突
        day = info["星期"]
        period = info["时间段"]

        # 检查公共位置是否有冲突
        if day in public_positions and period in public_positions[day]:
            fitness_score -= 1  # 如果与公共位置冲突，扣分
        else:
            fitness_score += 1  # 没有冲突，加分

    return fitness_score


def select(population, class_data, public_positions):
    """
    选择操作，根据适应度选择优秀的个体
    """
    population.sort(key=lambda x: fitness(x, class_data, public_positions), reverse=True)  # 按适应度排序
    return population[:int(population_size * 0.2)]  # 选择前20%的解


def crossover(parent1, parent2):
    """
    交叉操作，生成两个新的子代
    """
    child1 = parent1.copy()
    child2 = parent2.copy()
    for key in parent1.keys():
        if random.random() < 0.5:  # 以一定概率交换排课
            child1[key], child2[key] = child2[key], child1[key]
    return child1, child2


def mutate(schedule):
    """
    变异操作，对排课方案进行随机变异
    """
    for key in schedule.keys():
        if random.random() < mutation_rate:  # 以一定概率进行变异
            schedule[key] = {
                "星期": random.choice(parameter.week),
                "时间段": random.choice(parameter.classes),
                "教室": random.choice(parameter.place)
            }
    return schedule


def genetic_algorithm(class_data, public_positions):
    """
    遗传算法主函数，执行排课优化
    """
    population = initialize_population(population_size, class_data)  # 初始化种群
    for _ in range(generations):  # 进行指定次数的迭代
        selected_population = select(population, class_data, public_positions)  # 选择操作
        children = []
        for _ in range(population_size // 2):  # 生成新的子代
            parent1, parent2 = random.sample(selected_population, 2)  # 随机选择两个父代
            child1, child2 = crossover(parent1, parent2)  # 交叉操作
            children.extend([mutate(child1), mutate(child2)])  # 变异操作
        population = children  # 更新种群
    best_schedule = population[0]  # 选择最优解
    last_schedule = final_result(class_data, best_schedule)
    return last_schedule


def final_result(class_data, best_schedule):
    """
    补全排课结果，添加起止周和学分信息
    """
    # 遍历排课结果，补全起止周和学分信息
    for (teacher, course), info in best_schedule.items():
        if teacher in class_data and course in class_data[teacher]:
            course_info = class_data[teacher][course]
            # 添加起止周信息
            info["起止周"] = course_info["起止周"]
            # 添加学分信息
            info["学分"] = course_info["学分"]

    return best_schedule
