def performance_by_users(contest_id):
    return [
        ('handle', 1500, 'A', 200),('handle', 1500, 'B', 300),('handle', 1500, 'E', 300),
        ('handle_2', 1700, 'A', 100), ('handle_2', 1700, 'B', 300),('handle_2', 1700, 'C', 500), ('handle_2', 1500, 'E', 300)
    ]

def contest_performance_stats(contest_id):
    users_performance = performance_by_users(contest_id)

    return [{
        'A': [(1000, 300),(1100, 210), (1200, 220)],
        'B': [(1000, 400), (1100, 310), (1200, 220)],
        'C': [(1000, 600), (1100, 520), (1200, 220)],
        'D': [(1000, 500), (1100, 310), (1200, 220)],
    }]


def task_performance_stats(contest_id, index):
    return {
        'performanceData':[{'rating':1000, 'time':2000},{'rating':1100, 'time':1300},{'rating':1200, 'time':800},{'rating':1300, 'time':600},{'rating':1400, 'time':300},{'rating':1500, 'time':200}],
        'name':'Super puper cool task'
    }
